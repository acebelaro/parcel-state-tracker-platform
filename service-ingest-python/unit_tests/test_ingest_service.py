"""
Unit tests for Telemetry Ingestion Service

This module provides comprehensive unit tests for the TelemetryIngestionService class,
including tests for save_telemetry_data, is_healthy, and GPS validation.
"""

import unittest
from unittest.mock import MagicMock, patch

from service.ingest_service import (
    TelemetryIngestionService,
    SaveTelemetryError,
    SaveTelemetryInvalidDataError,
    SaveTelemetryInvalidGpsDataError,
)
from service.data.telemetry_data import TelemetryData
from service.data.data_table import DataTable


class TestTelemetryIngestionService(unittest.TestCase):
    """Test cases for TelemetryIngestionService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_data_table = MagicMock(spec=DataTable)
        self.service = TelemetryIngestionService(data_table=self.mock_data_table)

        self.valid_telemetry_data = {
            "parcel_id": "A1B2C3D4",
            "device_id": "STM32_NUCLEO_01",
            "temperature": 22.4,
            "tilt_x": 12.1,
            "tilt_y": -3.5,
            "latitude": 13.1394,
            "longitude": 122.7483,
        }

    def test_save_telemetry_data_success(self):
        """Test successful telemetry data saving."""
        self.mock_data_table.save_telemetry.return_value = "507f1f77bcf86cd799439011"

        result = self.service.save_telemetry_data(self.valid_telemetry_data)

        self.assertIsInstance(result, TelemetryData)
        self.assertEqual(result.parcel_id, "A1B2C3D4")
        self.assertEqual(result.device_id, "STM32_NUCLEO_01")
        self.assertEqual(result.temperature, 22.4)
        self.assertEqual(result.tilt_x, 12.1)
        self.assertEqual(result.tilt_y, -3.5)
        self.assertEqual(result.latitude, 13.1394)
        self.assertEqual(result.longitude, 122.7483)

        self.mock_data_table.save_telemetry.assert_called_once()

    def test_save_telemetry_data_none_raises_invalid_data_error(self):
        """Test that None data raises SaveTelemetryInvalidDataError."""
        with self.assertRaises(SaveTelemetryInvalidDataError):
            self.service.save_telemetry_data(None)

    def test_save_telemetry_data_missing_field_raises_invalid_data_error(self):
        """Test that missing required field raises SaveTelemetryInvalidDataError."""
        invalid_data = {
            "parcel_id": "A1B2C3D4",
            # Missing device_id
            "temperature": 22.4,
            "tilt_x": 12.1,
            "tilt_y": -3.5,
            "latitude": 13.1394,
            "longitude": 122.7483,
        }

        with self.assertRaises(SaveTelemetryInvalidDataError):
            self.service.save_telemetry_data(invalid_data)

    def test_save_telemetry_data_invalid_temperature_raises_error(self):
        """Test that invalid temperature raises SaveTelemetryInvalidDataError."""
        invalid_data = self.valid_telemetry_data.copy()
        invalid_data["temperature"] = 300.0  # Above max allowed value

        with self.assertRaises(SaveTelemetryInvalidDataError):
            self.service.save_telemetry_data(invalid_data)

    def test_save_telemetry_data_invalid_latitude_raises_error(self):
        """Test that invalid latitude raises SaveTelemetryInvalidDataError."""
        invalid_data = self.valid_telemetry_data.copy()
        invalid_data["latitude"] = 100.0  # Above max allowed value

        with self.assertRaises(SaveTelemetryInvalidDataError):
            self.service.save_telemetry_data(invalid_data)

    def test_save_telemetry_data_invalid_longitude_raises_error(self):
        """Test that invalid longitude raises SaveTelemetryInvalidDataError."""
        invalid_data = self.valid_telemetry_data.copy()
        invalid_data["longitude"] = 200.0  # Above max allowed value

        with self.assertRaises(SaveTelemetryInvalidDataError):
            self.service.save_telemetry_data(invalid_data)

    def test_save_telemetry_data_unlocked_gps_raises_error(self):
        """Test that unlocked GPS (both lat/lng 0.0) raises SaveTelemetryInvalidGpsDataError."""
        unlocked_gps_data = self.valid_telemetry_data.copy()
        unlocked_gps_data["latitude"] = 0.0
        unlocked_gps_data["longitude"] = 0.0

        with self.assertRaises(SaveTelemetryInvalidGpsDataError):
            self.service.save_telemetry_data(unlocked_gps_data)

    def test_save_telemetry_data_zero_latitude_valid(self):
        """Test that zero latitude with non-zero longitude is valid (GPS on equator)."""
        equator_data = self.valid_telemetry_data.copy()
        equator_data["latitude"] = 0.0
        equator_data["longitude"] = 122.7483

        # Should not raise - this is valid GPS data
        result = self.service.save_telemetry_data(equator_data)
        self.assertIsInstance(result, TelemetryData)

    def test_save_telemetry_data_zero_longitude_valid(self):
        """Test that zero longitude with non-zero latitude is valid (GPS on prime meridian)."""
        meridian_data = self.valid_telemetry_data.copy()
        meridian_data["latitude"] = 13.1394
        meridian_data["longitude"] = 0.0

        # Should not raise - this is valid GPS data
        result = self.service.save_telemetry_data(meridian_data)
        self.assertIsInstance(result, TelemetryData)

    def test_save_telemetry_data_calls_data_table_once(self):
        """Test that save_telemetry_data calls data_table.save_telemetry exactly once."""
        self.mock_data_table.save_telemetry.return_value = "doc_id"

        self.service.save_telemetry_data(self.valid_telemetry_data)

        self.mock_data_table.save_telemetry.assert_called_once()

    def test_is_healthy_returns_true_when_connected(self):
        """Test is_healthy returns True when data table is connected."""
        self.mock_data_table.is_connected.return_value = True

        result = self.service.is_healthy()

        self.assertTrue(result)
        self.mock_data_table.is_connected.assert_called_once()

    def test_is_healthy_returns_false_when_disconnected(self):
        """Test is_healthy returns False when data table is disconnected."""
        self.mock_data_table.is_connected.return_value = False

        result = self.service.is_healthy()

        self.assertFalse(result)
        self.mock_data_table.is_connected.assert_called_once()

    def test_validate_gps_coordinates_with_valid_coordinates(self):
        """Test _validate_gps_coordinates with valid non-zero coordinates."""
        result = TelemetryIngestionService._validate_gps_coordinates(10.0, 20.0)
        self.assertTrue(result)

    def test_validate_gps_coordinates_with_zero_latitude_only(self):
        """Test _validate_gps_coordinates with zero latitude only."""
        result = TelemetryIngestionService._validate_gps_coordinates(0.0, 20.0)
        self.assertTrue(result)

    def test_validate_gps_coordinates_with_zero_longitude_only(self):
        """Test _validate_gps_coordinates with zero longitude only."""
        result = TelemetryIngestionService._validate_gps_coordinates(10.0, 0.0)
        self.assertTrue(result)

    def test_validate_gps_coordinates_with_both_zero(self):
        """Test _validate_gps_coordinates returns False when both are zero."""
        result = TelemetryIngestionService._validate_gps_coordinates(0.0, 0.0)
        self.assertFalse(result)

    def test_validate_gps_coordinates_with_negative_coordinates(self):
        """Test _validate_gps_coordinates with negative coordinates (valid)."""
        result = TelemetryIngestionService._validate_gps_coordinates(-10.0, -20.0)
        self.assertTrue(result)

    def test_save_telemetry_data_with_boundary_values(self):
        """Test save_telemetry_data with valid boundary values."""
        boundary_data = {
            "parcel_id": "A",  # Min length
            "device_id": "D",  # Min length
            "temperature": -100.0,  # Min temp
            "tilt_x": -180.0,  # Min tilt
            "tilt_y": -180.0,  # Min tilt
            "latitude": -90.0,  # Min lat
            "longitude": -180.0,  # Min long
        }

        result = self.service.save_telemetry_data(boundary_data)
        self.assertIsInstance(result, TelemetryData)
        self.assertEqual(result.temperature, -100.0)

    def test_save_telemetry_data_with_max_values(self):
        """Test save_telemetry_data with valid maximum values."""
        max_data = {
            "parcel_id": "A" * 50,  # Max length
            "device_id": "D" * 100,  # Max length
            "temperature": 200.0,  # Max temp
            "tilt_x": 180.0,  # Max tilt
            "tilt_y": 180.0,  # Max tilt
            "latitude": 90.0,  # Max lat
            "longitude": 180.0,  # Max long
        }

        result = self.service.save_telemetry_data(max_data)
        self.assertIsInstance(result, TelemetryData)
        self.assertEqual(result.temperature, 200.0)

    def test_exception_classes_inheritance(self):
        """Test that exception classes properly inherit from SaveTelemetryError."""
        self.assertTrue(issubclass(SaveTelemetryInvalidDataError, SaveTelemetryError))
        self.assertTrue(issubclass(SaveTelemetryInvalidGpsDataError, SaveTelemetryError))

    def test_invalid_data_error_message(self):
        """Test SaveTelemetryInvalidDataError has correct message."""
        error = SaveTelemetryInvalidDataError()
        self.assertEqual(str(error), "Invalid Data")

    def test_invalid_gps_error_message(self):
        """Test SaveTelemetryInvalidGpsDataError has correct message."""
        error = SaveTelemetryInvalidGpsDataError()
        expected_message = "Invalid GPS coordinates: both latitude and longitude cannot be 0.0 (un-locked GPS)"
        self.assertIn(expected_message, str(error))


class TestTelemetryIngestionServiceIntegration(unittest.TestCase):
    """Integration tests with mocked data table."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_data_table = MagicMock(spec=DataTable)
        self.service = TelemetryIngestionService(data_table=self.mock_data_table)

    def test_full_ingestion_workflow(self):
        """Test full ingestion workflow with mocked data table."""
        telemetry_data = {
            "parcel_id": "TEST123",
            "device_id": "DEVICE_01",
            "temperature": 25.5,
            "tilt_x": 5.0,
            "tilt_y": 3.0,
            "latitude": 14.5995,
            "longitude": 120.9842,
        }

        self.mock_data_table.save_telemetry.return_value = "mock_doc_id"

        # Save telemetry
        result = self.service.save_telemetry_data(telemetry_data)
        self.assertIsInstance(result, TelemetryData)

        # Check health
        self.mock_data_table.is_connected.return_value = True
        self.assertTrue(self.service.is_healthy())


if __name__ == "__main__":
    unittest.main()