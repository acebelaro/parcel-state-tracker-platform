"""
Python Ingest Service - Parcel State Tracker Platform

Lightweight asynchronous Python ingestion microservice for handling
high-throughput telemetry data from IoT edge devices.
"""

import os
from typing import Optional
from flask import Flask, request, jsonify

# from pymongo import MongoClient
from dotenv import load_dotenv

from data.data_table import DataTable
from data.telemetry_data import TelemetryData
from data.mongo.mongo_data_table import MongoDataTable

# Load environment variables
load_dotenv()

# Flask application initialization
app = Flask(__name__)

FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

# Maximum tracking entries per parcel (-1 for unlimited/no purge)
MAX_TRACKING_ENTRIES = int(os.getenv("MAX_TRACKING_ENTRIES", 10))


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
data_table: Optional[DataTable] = None
db = None


def get_data_table() -> DataTable:
    """Get or create MongoDB client connection."""
    global data_table
    if data_table is None:
        data_table = MongoDataTable(max_tracking_entries=MAX_TRACKING_ENTRIES)
    return data_table


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

        data_table = get_data_table()
        document_id = data_table.save_telemetry(telemetry=telemetry)

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
    mongo_status = "connected"
    data_table = get_data_table()
    if not data_table.is_connected():
        mongo_status = "disconnected"

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

    # Log startup information
    print(f"[STARTUP] Starting Python Ingest Service...")
    print(f"[STARTUP] Flask Environment: {FLASK_ENV}")
    print(f"[STARTUP] Port: {FLASK_PORT}")
    print(
        f"[STARTUP] Max Tracking Entries: {'unlimited' if MAX_TRACKING_ENTRIES == -1 else MAX_TRACKING_ENTRIES}"
    )

    # Test MongoDB connection
    try:
        data_table = get_data_table()
        _ = data_table.is_connected()
        print("[STARTUP] MongoDB connection: OK")
    except Exception as e:
        print(f"[STARTUP] MongoDB connection: FAILED - {str(e)}")
        print("[STARTUP] WARNING: Service will start but database operations may fail")

    # Run Flask application
    debug_mode = FLASK_ENV == "development"
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=debug_mode)
