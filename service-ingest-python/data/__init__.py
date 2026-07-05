"""
Data Package

This package provides data models and storage abstractions for parcel telemetry data.
It includes Pydantic models for data validation and abstract/base classes for
implementing data persistence across different storage backends.
"""

from .telemetry_data import TelemetryData
from .data_table import DataTable, TelemetrySavingError, TelemetryTableCreationError

__all__ = [
    "TelemetryData",
    "DataTable",
    "TelemetrySavingError",
    "TelemetryTableCreationError",
]