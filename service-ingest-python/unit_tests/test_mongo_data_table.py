"""
Unit tests for MongoDB Data Table Implementation

This module provides comprehensive unit tests for the MongoDataTable class,
including tests for save_telemetry, is_connected, and URI building functionality.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from pymongo.errors import ConnectionFailure, OperationFailure

from service.data.telemetry_data import TelemetryData
from service.data.data_table import TelemetrySavingError, TelemetryTableCreationError
from service.data.mongo.mongo_data_table import MongoDataTable


class TestMongoDataTable(unittest.TestCase):
    """Test cases for MongoDataTable class."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_telemetry_data = TelemetryData(
            parcel_id="A1B2C3D4",
            device_id="STM32_NUCLEO_01",
            temperature=22.4,
            tilt_x=12.1,
            tilt_y=-3.5,
            latitude=13.1394,
            longitude=122.7483,
        )

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_init_success(self, mock_mongo_client):
        """Test successful initialization of MongoDataTable."""
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance

        table = MongoDataTable(max_tracking_entries=10)

        self.assertEqual(table._max_tracking_entries, 10)
        mock_mongo_client.assert_called_once()

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_init_connection_failure_raises_error(self, mock_mongo_client):
        """Test that connection failure raises TelemetryTableCreationError."""
        mock_mongo_client.side_effect = ConnectionFailure("Connection refused")

        with self.assertRaises(TelemetryTableCreationError) as context:
            MongoDataTable(max_tracking_entries=10)

        self.assertIn("Connection refused", str(context.exception))

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_init_generic_exception_raises_error(self, mock_mongo_client):
        """Test that generic exception during init raises TelemetryTableCreationError."""
        mock_mongo_client.side_effect = Exception("Unexpected error")

        with self.assertRaises(TelemetryTableCreationError) as context:
            MongoDataTable(max_tracking_entries=10)

        self.assertIn("Unexpected error", str(context.exception))

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_build_mongodb_uri_without_auth(self, mock_mongo_client):
        """Test MongoDB URI building without authentication credentials."""
        with patch.dict(
            "os.environ",
            {"MONGODB_HOST": "localhost", "MONGODB_PORT": "27017"},
            clear=True,
        ):
            import importlib
            import service.data.mongo.mongo_data_table as mongo_module

            importlib.reload(mongo_module)

            uri = mongo_module.MongoDataTable._build_mongodb_uri()

            self.assertEqual(uri, "mongodb://localhost:27017/")

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_build_mongodb_uri_with_auth(self, mock_mongo_client):
        """Test MongoDB URI building with authentication credentials."""
        with patch.dict(
            "os.environ",
            {
                "MONGODB_HOST": "mongo.example.com",
                "MONGODB_PORT": "27017",
                "MONGODB_USERNAME": "admin@user",
                "MONGODB_PASSWORD": "p@ssw0rd",
                "MONGODB_AUTH_SOURCE": "admin",
            },
        ):
            import importlib
            import service.data.mongo.mongo_data_table as mongo_module

            importlib.reload(mongo_module)

            uri = mongo_module.MongoDataTable._build_mongodb_uri()

            self.assertIn("admin%40user", uri)
            self.assertIn("p%40ssw0rd", uri)
            self.assertIn("authSource=admin", uri)

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_save_telemetry_creates_new_document(self, mock_mongo_client):
        """Test saving telemetry creates a new parcel document when it doesn't exist."""
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        # Simulate document not existing
        mock_collection.find_one.return_value = None
        mock_collection.find_one_and_update.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "parcel_id": "A1B2C3D4",
            "tracking": [],
        }

        table = MongoDataTable(max_tracking_entries=10)
        result = table.save_telemetry(self.valid_telemetry_data)

        # Verify find_one was called with parcel_id
        mock_collection.find_one.assert_called_once_with({"parcel_id": "A1B2C3D4"})

        # Verify find_one_and_update was called with upsert
        mock_collection.find_one_and_update.assert_called_once()
        call_args = mock_collection.find_one_and_update.call_args
        self.assertEqual(call_args[0][0], {"parcel_id": "A1B2C3D4"})
        self.assertTrue(call_args[1].get("upsert", False))

        # Verify result is the document ID
        self.assertEqual(result, "507f1f77bcf86cd799439011")

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_save_telemetry_updates_existing_document(self, mock_mongo_client):
        """Test saving telemetry updates an existing parcel document."""
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        # Simulate document already existing
        existing_doc = {
            "_id": "507f1f77bcf86cd799439011",
            "parcel_id": "A1B2C3D4",
            "tracking": [{"temperature": 20.0}],
        }
        mock_collection.find_one.return_value = existing_doc
        mock_collection.find_one_and_update.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "parcel_id": "A1B2C3D4",
            "tracking": [{"temperature": 22.4}],
        }

        table = MongoDataTable(max_tracking_entries=10)
        result = table.save_telemetry(self.valid_telemetry_data)

        # Verify update operation was called (without upsert)
        call_args = mock_collection.find_one_and_update.call_args
        self.assertEqual(call_args[0][0], {"parcel_id": "A1B2C3D4"})
        self.assertNotIn("upsert", call_args[1])

        # Verify $push operation exists
        update_op = call_args[0][1]
        self.assertIn("$push", update_op)

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_save_telemetry_with_max_entries_apply_slice(self, mock_mongo_client):
        """Test that max_tracking_entries applies slice to update operation."""
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        existing_doc = {"parcel_id": "A1B2C3D4", "tracking": []}
        mock_collection.find_one.return_value = existing_doc
        mock_collection.find_one_and_update.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "parcel_id": "A1B2C3D4",
            "tracking": [],
        }

        table = MongoDataTable(max_tracking_entries=5)
        table.save_telemetry(self.valid_telemetry_data)

        call_args = mock_collection.find_one_and_update.call_args
        update_op = call_args[0][1]

        # Verify slice is applied when max_tracking_entries > 0
        self.assertEqual(update_op["$push"]["tracking"]["$slice"], 5)

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_save_telemetry_without_max_entries_no_slice(self, mock_mongo_client):
        """Test that unlimited entries (-1) does not apply slice."""
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        existing_doc = {"parcel_id": "A1B2C3D4", "tracking": []}
        mock_collection.find_one.return_value = existing_doc
        mock_collection.find_one_and_update.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "parcel_id": "A1B2C3D4",
            "tracking": [],
        }

        table = MongoDataTable(max_tracking_entries=-1)
        table.save_telemetry(self.valid_telemetry_data)

        call_args = mock_collection.find_one_and_update.call_args
        update_op = call_args[0][1]

        # Verify slice is NOT applied when max_tracking_entries <= 0
        self.assertNotIn("$slice", update_op["$push"]["tracking"])

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_save_telemetry_operation_failure_raises_error(self, mock_mongo_client):
        """Test that operation failure raises TelemetrySavingError."""
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        mock_collection.find_one.return_value = None
        mock_collection.find_one_and_update.side_effect = OperationFailure("Write error")

        table = MongoDataTable(max_tracking_entries=10)

        with self.assertRaises(TelemetrySavingError) as context:
            table.save_telemetry(self.valid_telemetry_data)

        self.assertIn("Write error", str(context.exception))

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_save_telemetry_generic_failure_raises_error(self, mock_mongo_client):
        """Test that generic exception raises TelemetrySavingError."""
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        mock_collection.find_one.return_value = None
        mock_collection.find_one_and_update.side_effect = Exception("Database error")

        table = MongoDataTable(max_tracking_entries=10)

        with self.assertRaises(TelemetrySavingError) as context:
            table.save_telemetry(self.valid_telemetry_data)

        self.assertIn("Database error", str(context.exception))

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_save_telemetry_returns_parcel_id_on_no_result(self, mock_mongo_client):
        """Test that save_telemetry returns parcel_id when no result returned."""
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        mock_collection.find_one.return_value = None
        mock_collection.find_one_and_update.return_value = None

        table = MongoDataTable(max_tracking_entries=10)
        result = table.save_telemetry(self.valid_telemetry_data)

        # Should return parcel_id as fallback
        self.assertEqual(result, "A1B2C3D4")

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_is_connected_returns_true(self, mock_mongo_client):
        """Test is_connected returns True when MongoDB is reachable."""
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        mock_admin = MagicMock()
        mock_client_instance.admin = mock_admin
        mock_admin.command.return_value = {"ok": 1}

        table = MongoDataTable(max_tracking_entries=10)
        result = table.is_connected()

        self.assertTrue(result)
        mock_admin.command.assert_called_once_with("ping")

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_is_connected_returns_false_on_connection_failure(self, mock_mongo_client):
        """Test is_connected returns False on connection failure."""
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        mock_admin = MagicMock()
        mock_client_instance.admin = mock_admin
        mock_admin.command.side_effect = ConnectionFailure("Ping failed")

        table = MongoDataTable(max_tracking_entries=10)
        result = table.is_connected()

        self.assertFalse(result)

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_is_connected_returns_false_on_exception(self, mock_mongo_client):
        """Test is_connected returns False on any exception."""
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        mock_admin = MagicMock()
        mock_client_instance.admin = mock_admin
        mock_admin.command.side_effect = Exception("Unknown error")

        table = MongoDataTable(max_tracking_entries=10)
        result = table.is_connected()

        self.assertFalse(result)

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_tracking_entry_contains_all_fields(self, mock_mongo_client):
        """Test that tracking entry contains all telemetry data fields."""
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        mock_collection.find_one.return_value = None
        mock_collection.find_one_and_update.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "parcel_id": "A1B2C3D4",
            "tracking": [],
        }

        table = MongoDataTable(max_tracking_entries=10)
        table.save_telemetry(self.valid_telemetry_data)

        # Extract the update call to verify tracking entry structure
        call_args = mock_collection.find_one_and_update.call_args
        update_op = call_args[0][1]
        set_on_insert = update_op["$setOnInsert"]
        tracking_entry = set_on_insert["tracking"][0]

        # Verify all fields are present
        self.assertEqual(tracking_entry["temperature"], 22.4)
        self.assertEqual(tracking_entry["tilt_x"], 12.1)
        self.assertEqual(tracking_entry["tilt_y"], -3.5)
        self.assertEqual(tracking_entry["latitude"], 13.1394)
        self.assertEqual(tracking_entry["longitude"], 122.7483)
        self.assertIn("timestamp", tracking_entry)

    @patch("service.data.mongo.mongo_data_table.MongoClient")
    def test_tracking_entry_uses_utc_timestamp(self, mock_mongo_client):
        """Test that tracking entry uses UTC timezone for timestamp."""
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        mock_collection.find_one.return_value = None
        mock_collection.find_one_and_update.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "parcel_id": "A1B2C3D4",
            "tracking": [],
        }

        table = MongoDataTable(max_tracking_entries=10)
        table.save_telemetry(self.valid_telemetry_data)

        # Extract the tracking entry
        call_args = mock_collection.find_one_and_update.call_args
        update_op = call_args[0][1]
        set_on_insert = update_op["$setOnInsert"]
        tracking_entry = set_on_insert["tracking"][0]

        # Verify timestamp has UTC timezone
        timestamp = tracking_entry["timestamp"]
        self.assertEqual(timestamp.tzinfo, timezone.utc)


class TestMongoDataTableIntegration(unittest.TestCase):
    """Integration tests for MongoDataTable (require MongoDB instance)."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_telemetry_data = TelemetryData(
            parcel_id="A1B2C3D4",
            device_id="STM32_NUCLEO_01",
            temperature=22.4,
            tilt_x=12.1,
            tilt_y=-3.5,
            latitude=13.1394,
            longitude=122.7483,
        )

    def test_full_workflow_with_mock(self):
        """Test full save and query workflow with mocked database."""
        with patch("service.data.mongo.mongo_data_table.MongoClient") as mock_mongo_client:
            mock_client_instance = MagicMock()
            mock_mongo_client.return_value = mock_client_instance
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_client_instance.__getitem__.return_value = mock_db
            mock_db.__getitem__.return_value = mock_collection

            table = MongoDataTable(max_tracking_entries=10)

            # First save - creates document
            mock_collection.find_one.return_value = None
            mock_collection.find_one_and_update.return_value = {
                "_id": "507f1f77bcf86cd799439011",
                "parcel_id": "A1B2C3D4",
                "tracking": [],
            }

            result1 = table.save_telemetry(self.valid_telemetry_data)
            self.assertIsNotNone(result1)

            # Verify connection check works
            mock_admin = MagicMock()
            mock_client_instance.admin = mock_admin
            mock_admin.command.return_value = {"ok": 1}
            self.assertTrue(table.is_connected())


if __name__ == "__main__":
    unittest.main()