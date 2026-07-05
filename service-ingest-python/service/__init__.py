"""
Service Package

This package provides core services for the Parcel State Tracker Platform.
Currently includes the telemetry ingestion service for IoT data processing.
"""

from .ingest_service import (
    TelemetryIngestionService,
    SaveTelemetryError,
    SaveTelemetryInvalidDataError,
    SaveTelemetryInvalidGpsDataError,
)

__all__ = [
    "TelemetryIngestionService",
    "SaveTelemetryError",
    "SaveTelemetryInvalidDataError",
    "SaveTelemetryInvalidGpsDataError",
]
