"""
MongoDB Data Table Implementation Package

This package provides the MongoDB implementation of the DataTable abstraction
for persisting parcel telemetry data.
"""

from .mongo_data_table import MongoDataTable

__all__ = ["MongoDataTable"]