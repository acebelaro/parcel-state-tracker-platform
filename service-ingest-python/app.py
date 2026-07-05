"""
Python Ingest Service - Parcel State Tracker Platform

Lightweight asynchronous Python ingestion microservice for handling
high-throughput telemetry data from IoT edge devices.
"""

import os
import logging
from typing import Optional
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from service.data.mongo.mongo_data_table import MongoDataTable
from service.ingest_service import TelemetryIngestionService, SaveTelemetryError

# Load environment variables
load_dotenv()

# Flask application initialization
app = Flask(__name__)

LOGGER = logging.getLogger(__name__)

FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

# Maximum tracking entries per parcel (-1 for unlimited/no purge)
MAX_TRACKING_ENTRIES = int(os.getenv("MAX_TRACKING_ENTRIES", 10))


ingestion_service: Optional[TelemetryIngestionService] = None


def get_service() -> TelemetryIngestionService:
    global ingestion_service
    if ingestion_service is None:
        data_table = MongoDataTable(max_tracking_entries=MAX_TRACKING_ENTRIES)
        ingestion_service = TelemetryIngestionService(data_table=data_table)
    return ingestion_service


@app.route("/api/v1/ingest", methods=["POST"])
def ingest_telemetry():
    """
    Ingest telemetry data from IoT edge devices.

    This endpoint receives JSON payloads from IoT devices, validates the data,
    adds server-side metadata, and stores it in database.

    Returns:
        JSON response with status and parcel ID on success,
        or error details on failure.
    """
    try:
        # Parse JSON payload
        data = request.get_json()

        ingestion_service = get_service()
        telemetry_data = ingestion_service.save_telemetry_data(data=data)

        # Log successful ingestion
        print(
            f"[INGEST] Successfully ingested telemetry for parcel {telemetry_data.parcel_id}, "
        )

        # Return success response
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Telemetry data ingested successfully",
                    "parcel_id": telemetry_data.parcel_id,
                }
            ),
            200,
        )
    except Exception as e:
        if not isinstance(e, SaveTelemetryError):
            # Log error
            LOGGER.error(f"Failed to ingest telemetry due to unknown error: {str(e)}")
        else:
            LOGGER.error(str(e))

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
    service_status = "connected"
    ingestion_service = get_service()
    if not ingestion_service.is_healthy():
        service_status = "disconnected"

    return (
        jsonify(
            {
                "service_status": service_status,
                "service": "python-ingest-service",
                "version": "1.0.0",
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

    # Test Database connection
    try:
        ingestion_service = get_service()
        _ = ingestion_service.is_healthy()
        print("[STARTUP] Database connection: OK")
    except Exception as e:
        print(f"[STARTUP] Database connection: FAILED - {str(e)}")
        print("[STARTUP] WARNING: Service will start but database operations may fail")

    # Run Flask application
    debug_mode = FLASK_ENV == "development"
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=debug_mode)
