"""
Python Ingest Service - Parcel State Tracker Platform

Lightweight asynchronous Python ingestion microservice for handling
high-throughput telemetry data from IoT edge devices.
"""

import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from pydantic import BaseModel, Field, field_validator, ConfigDict
from pymongo import MongoClient
from dotenv import load_dotenv

from data.mongo.mongo_table import MongoTable

# Load environment variables
load_dotenv()

# Flask application initialization
app = Flask(__name__)

# Configuration from environment variables
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
MONGODB_PORT = int(os.getenv("MONGODB_PORT", 27017))
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME", "")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "parcel_tracker")
MONGODB_AUTH_SOURCE = os.getenv("MONGODB_AUTH_SOURCE", "admin")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

# Maximum tracking entries per parcel (-1 for unlimited/no purge)
MAX_TRACKING_ENTRIES = int(os.getenv("MAX_TRACKING_ENTRIES", 10))


# Build MongoDB URI with authentication if credentials are provided
def build_mongodb_uri():
    """Build MongoDB connection URI with optional authentication."""
    if MONGODB_USERNAME and MONGODB_PASSWORD:
        from urllib.parse import quote_plus

        encoded_username = quote_plus(MONGODB_USERNAME)
        encoded_password = quote_plus(MONGODB_PASSWORD)
        return f"mongodb://{encoded_username}:{encoded_password}@{MONGODB_HOST}:{MONGODB_PORT}/?authSource={MONGODB_AUTH_SOURCE}"
    else:
        return f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}/"


MONGODB_URI = build_mongodb_uri()


# Pydantic model for telemetry data validation
class TelemetryData(BaseModel):
    """Schema for incoming telemetry data from IoT edge devices."""

    parcel_id: str = Field(
        ..., min_length=1, max_length=50, description="Unique parcel identifier"
    )
    device_id: str = Field(
        ..., min_length=1, max_length=100, description="Device identifier"
    )
    temperature: float = Field(
        ..., ge=-100.0, le=200.0, description="Temperature reading in Celsius"
    )
    tilt_x: float = Field(
        ..., ge=-180.0, le=180.0, description="Tilt angle on X-axis in degrees"
    )
    tilt_y: float = Field(
        ..., ge=-180.0, le=180.0, description="Tilt angle on Y-axis in degrees"
    )
    latitude: float = Field(
        ..., ge=-90.0, le=90.0, description="GPS latitude coordinate"
    )
    longitude: float = Field(
        ..., ge=-180.0, le=180.0, description="GPS longitude coordinate"
    )

    @field_validator("latitude", "longitude")
    @classmethod
    def validate_gps_not_zero(cls, v, info):
        """Validate that GPS coordinates are not both zero (un-locked GPS)."""
        # This validation will be done in the main validation check
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "parcel_id": "A1B2C3D4",
                "device_id": "STM32_NUCLEO_01",
                "temperature": 22.4,
                "tilt_x": 12.1,
                "tilt_y": -3.5,
                "latitude": 13.1394,
                "longitude": 122.7483,
            }
        }
    )


def validate_gps_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate that GPS coordinates are not both zero (indicating un-locked GPS).

    Args:
        latitude: GPS latitude coordinate
        longitude: GPS longitude coordinate

    Returns:
        True if coordinates are valid, False if both are zero
    """
    return not (latitude == 0.0 and longitude == 0.0)


# MongoDB connection
mongo_client = None
db = None


def get_mongo_client():
    """Get or create MongoDB client connection."""
    global mongo_client
    if mongo_client is None:
        mongo_client = MongoClient(MONGODB_URI)
    return mongo_client


def get_db():
    """Get database instance."""
    global db
    if db is None:
        client = get_mongo_client()
        db = client[MONGODB_DB_NAME]
    return db


def get_collection():
    """Get telemetry collection."""
    return get_db()["telemetry"]


def upsert_telemetry(telemetry: TelemetryData) -> str:
    """
    Upsert telemetry data with tracking array schema.

    Creates a new parcel document if it doesn't exist, or adds a new tracking
    entry to the existing parcel's tracking array. The newest tracking entry
    is always at index 0. If tracking array exceeds MAX_TRACKING_ENTRIES,
    the oldest entries are removed.

    Args:
        telemetry: Validated TelemetryData instance

    Returns:
        The MongoDB document ID (parcel_id)
    """
    collection = get_collection()

    # Create new tracking entry
    tracking_entry = {
        "temperature": telemetry.temperature,
        "tilt_x": telemetry.tilt_x,
        "tilt_y": telemetry.tilt_y,
        "latitude": telemetry.latitude,
        "longitude": telemetry.longitude,
        "timestamp": datetime.now(timezone.utc),
    }

    # Check if document exists - if not, create with initial tracking array
    existing = collection.find_one({"parcel_id": telemetry.parcel_id})

    if existing:
        # Update existing document - push new tracking at index 0 with slice
        # If MAX_TRACKING_ENTRIES is -1, no slice is applied (unlimited entries)
        update_operation = {
            "$push": {"tracking": {"$each": [tracking_entry], "$position": 0}}
        }
        if MAX_TRACKING_ENTRIES > 0:
            update_operation["$push"]["tracking"]["$slice"] = MAX_TRACKING_ENTRIES

        result = collection.find_one_and_update(
            {"parcel_id": telemetry.parcel_id}, update_operation, return_document=True
        )
    else:
        # Create new document with tracking array
        result = collection.find_one_and_update(
            {"parcel_id": telemetry.parcel_id},
            {
                "$setOnInsert": {
                    "parcel_id": telemetry.parcel_id,
                    "tracking": [tracking_entry],
                }
            },
            upsert=True,
            return_document=True,
        )

    return str(result["_id"]) if result else telemetry.parcel_id


@app.route("/api/v1/ingest", methods=["POST"])
def ingest_telemetry():
    """
    Ingest telemetry data from IoT edge devices.

    This endpoint receives JSON payloads from IoT devices, validates the data,
    adds server-side metadata, and stores it in MongoDB.

    Returns:
        JSON response with status and document ID on success,
        or error details on failure.
    """
    try:
        # Parse JSON payload
        data = request.get_json()

        if data is None:
            return jsonify({"status": "error", "message": "Invalid JSON payload"}), 400

        # Validate payload using Pydantic
        try:
            telemetry = TelemetryData(**data)
        except ValueError as e:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Validation failed",
                        "details": str(e),
                    }
                ),
                400,
            )

        # Validate GPS coordinates (not both zero)
        if not validate_gps_coordinates(telemetry.latitude, telemetry.longitude):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Invalid GPS coordinates: both latitude and longitude cannot be 0.0 (un-locked GPS)",
                    }
                ),
                400,
            )

        # Upsert telemetry data with tracking array
        document_id = upsert_telemetry(telemetry)

        # Log successful ingestion
        print(
            f"[INGEST] Successfully ingested telemetry for parcel {telemetry.parcel_id}, "
            f"document_id: {document_id}"
        )

        # Return success response
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Telemetry data ingested successfully",
                    "document_id": document_id,
                }
            ),
            200,
        )

    except Exception as e:
        # Log error
        print(f"[ERROR] Failed to ingest telemetry: {str(e)}")

        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Internal server error",
                    "details": str(e) if FLASK_ENV == "development" else None,
                }
            ),
            500,
        )


@app.route("/api/v1/health", methods=["GET"])
def health_check():
    """
    Health check endpoint.

    Returns:
        JSON response indicating service health status.
    """
    try:
        # Check MongoDB connection
        client = get_mongo_client()
        client.admin.command("ping")
        mongo_status = "connected"
    except Exception as e:
        mongo_status = f"disconnected: {str(e)}"

    return (
        jsonify(
            {
                "status": "healthy",
                "service": "python-ingest-service",
                "version": "1.0.0",
                "mongodb": mongo_status,
            }
        ),
        200,
    )


@app.route("/", methods=["GET"])
def root():
    """
    Root endpoint with service information.

    Returns:
        JSON response with service details.
    """
    return (
        jsonify(
            {
                "service": "Python Ingest Service",
                "version": "1.0.0",
                "description": "IoT telemetry ingestion microservice for Parcel State Tracker Platform",
                "endpoints": {"ingest": "/api/v1/ingest", "health": "/api/v1/health"},
            }
        ),
        200,
    )


if __name__ == "__main__":

    mongo_table = MongoTable()

    # Log startup information
    print(f"[STARTUP] Starting Python Ingest Service...")
    print(f"[STARTUP] MongoDB URI: {MONGODB_URI}")
    print(f"[STARTUP] Database: {MONGODB_DB_NAME}")
    print(f"[STARTUP] Flask Environment: {FLASK_ENV}")
    print(f"[STARTUP] Port: {FLASK_PORT}")
    print(
        f"[STARTUP] Max Tracking Entries: {'unlimited' if MAX_TRACKING_ENTRIES == -1 else MAX_TRACKING_ENTRIES}"
    )

    # Test MongoDB connection
    try:
        client = get_mongo_client()
        client.admin.command("ping")
        print("[STARTUP] MongoDB connection: OK")
    except Exception as e:
        print(f"[STARTUP] MongoDB connection: FAILED - {str(e)}")
        print("[STARTUP] WARNING: Service will start but database operations may fail")

    # Run Flask application
    debug_mode = FLASK_ENV == "development"
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=debug_mode)
