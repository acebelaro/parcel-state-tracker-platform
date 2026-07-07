"""
MongoDB Data Table Implementation

This module provides the MongoDB implementation of the DataTable abstraction
for storing parcel telemetry data with support for tracking entry history.
"""

from datetime import datetime, timezone
import os
from pymongo import MongoClient

from ..telemetry_data import TelemetryData
from ..data_table import DataTable, TelemetrySavingError, TelemetryTableCreationError

# Configuration from environment variables
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
MONGODB_PORT = int(os.getenv("MONGODB_PORT", 27017))
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME", "")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "parcel_tracker")
MONGODB_AUTH_SOURCE = os.getenv("MONGODB_AUTH_SOURCE", "admin")


class MongoDataTable(DataTable):
    """MongoDB implementation of the telemetry data table.
    
    This class provides persistent storage for parcel telemetry data using MongoDB.
    Each parcel is stored as a document with a parcel_id and an array of tracking
    entries, where each entry contains temperature, tilt, GPS coordinates, and
    timestamp.
    
    Args:
        max_tracking_entries: Maximum number of tracking entries to keep per parcel.
            Use -1 for unlimited entries. Defaults to -1.
    
    Attributes:
        _mongo_uri: The MongoDB connection URI.
        _mongo_client: The PyMongo client instance.
        _max_tracking_entries: Maximum number of tracking entries per parcel.
    
    Environment Variables:
        MONGODB_HOST: MongoDB server hostname. Default: "localhost"
        MONGODB_PORT: MongoDB server port. Default: 27017
        MONGODB_USERNAME: MongoDB authentication username. Default: ""
        MONGODB_PASSWORD: MongoDB authentication password. Default: ""
        MONGODB_DB_NAME: Database name. Default: "parcel_tracker"
        MONGODB_AUTH_SOURCE: Authentication database source. Default: "admin"
    
    Raises:
        TelemetryTableCreationError: If the MongoDB connection cannot be established.
    """

    def __init__(
        self,
        max_tracking_entries: int,
    ):
        super().__init__(
            max_tracking_entries=max_tracking_entries,
        )
        try:
            self._mongo_uri = MongoDataTable._build_mongodb_uri()
            print(self._mongo_uri)
            self._mongo_client = MongoClient(self._mongo_uri)
            print(" >>> Created mongo client <<< ")
        except Exception as e:
            raise TelemetryTableCreationError(str(e))

    @property
    def _db(self):
        """Get the MongoDB database instance.
        
        Returns:
            The MongoDB database for parcel tracking data.
        """
        return self._mongo_client[MONGODB_DB_NAME]

    def save_telemetry(self, telemetry: TelemetryData) -> str:
        """Save telemetry data to MongoDB.
        
        Creates a new tracking entry for the parcel and updates the document.
        If the parcel document doesn't exist, it will be created. Existing tracking
        entries are maintained in chronological order (newest first), and the
        number of entries is limited by max_tracking_entries.
        
        Args:
            telemetry: The telemetry data to save.
            
        Returns:
            The MongoDB document ID as a string.
            
        Raises:
            TelemetrySavingError: If the save operation fails.
        """
        try:
            collection = self._db["telemetry"]

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
                # If max_tracking_entries is -1, no slice is applied (unlimited entries)
                update_operation = {
                    "$push": {"tracking": {"$each": [tracking_entry], "$position": 0}}
                }
                if self._max_tracking_entries > 0:
                    update_operation["$push"]["tracking"][
                        "$slice"
                    ] = self._max_tracking_entries

                result = collection.find_one_and_update(
                    {"parcel_id": telemetry.parcel_id},
                    update_operation,
                    return_document=True,
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
        except Exception as e:
            raise TelemetrySavingError(str(e))

    def is_connected(self) -> bool:
        """Check if the MongoDB connection is active.
        
        Tests the connection by sending a ping command to the MongoDB admin database.
        
        Returns:
            True if the connection is active and MongoDB is reachable, False otherwise.
        """
        try:
            self._mongo_client.admin.command("ping")
            return True
        except:
            return False

    @staticmethod
    def _build_mongodb_uri() -> str:
        """Build MongoDB connection URI with optional authentication.
        
        Constructs the appropriate MongoDB connection string based on the configured
        environment variables. If username and password are provided, they will be
        included in the URI with proper URL encoding.
        
        Returns:
            The MongoDB connection URI string.
        """
        if MONGODB_USERNAME and MONGODB_PASSWORD:
            from urllib.parse import quote_plus

            encoded_username = quote_plus(MONGODB_USERNAME)
            encoded_password = quote_plus(MONGODB_PASSWORD)
            return f"mongodb://{encoded_username}:{encoded_password}@{MONGODB_HOST}:{MONGODB_PORT}/?authSource={MONGODB_AUTH_SOURCE}"
        else:
            return f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}/"