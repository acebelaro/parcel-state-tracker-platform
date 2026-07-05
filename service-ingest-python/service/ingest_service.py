"""
Telemetry Ingestion Service

This module provides the core service for ingesting and validating telemetry data
from IoT edge devices in the Parcel State Tracker Platform.
"""

from typing import Any, Optional
from .data.telemetry_data import TelemetryData
from .data.data_table import DataTable


class SaveTelemetryError(Exception):
    """Exception raised when telemetry data cannot be saved successfully.

    This is the base exception class for all telemetry saving errors.
    It indicates that the ingestion process failed due to invalid data or
    other validation issues.

    Args:
        error: The error message describing why telemetry saving failed.
    """

    def __init__(self, error: str):
        super().__init__(error)


class SaveTelemetryInvalidDataError(SaveTelemetryError):
    """Exception raised when telemetry data fails validation.

    This exception is raised when the incoming payload fails Pydantic validation
    checks, such as missing required fields, invalid data types, or values outside
    the allowed ranges.

    The error message is automatically set to "Invalid Data".
    """

    def __init__(self):
        super().__init__(error="Invalid Data")


class SaveTelemetryInvalidGpsDataError(SaveTelemetryError):
    """Exception raised when GPS coordinates are invalid.

    This exception is raised when both latitude and longitude are 0.0,
    which indicates that the GPS module has not acquired a valid lock on
    the satellites. Such coordinates are not acceptable for tracking purposes.

    The error message is automatically set to indicate the GPS validation failure.
    """

    def __init__(self):
        super().__init__(
            error="Invalid GPS coordinates: both latitude and longitude cannot be 0.0 (un-locked GPS)"
        )


class TelemetryIngestionService:
    """Service for ingesting and validating telemetry data from IoT devices.

    This service handles the core logic for processing telemetry data from IoT edge devices,
    including Pydantic-based payload validation and GPS coordinate verification. It delegates
    the actual data persistence to a DataTable implementation, making it database-agnostic.

    Attributes:
        _data_table: The DataTable instance used for persisting telemetry data.

    Example:
        >>> from service.data.mongo.mongo_data_table import MongoDataTable
        >>> data_table = MongoDataTable(max_tracking_entries=10)
        >>> service = TelemetryIngestionService(data_table)
        >>> telemetry = service.save_telemetry_data({
        ...     "parcel_id": "A1B2C3D4",
        ...     "device_id": "STM32_NUCLEO_01",
        ...     "temperature": 22.4,
        ...     "tilt_x": 12.1,
        ...     "tilt_y": -3.5,
        ...     "latitude": 13.1394,
        ...     "longitude": 122.7483
        ... })
        >>> telemetry.parcel_id
        'A1B2C3D4'
    """

    def __init__(self, data_table: DataTable):
        """Initialize the TelemetryIngestionService.

        Args:
            data_table: A DataTable implementation for persisting telemetry data.
                Must implement save_telemetry() and is_connected() methods.
        """
        self._data_table = data_table

    def save_telemetry_data(self, data: Any) -> TelemetryData:
        """Save telemetry data from an IoT device after validation.

        This method validates the incoming data payload, checks GPS coordinates,
        and persists the telemetry data to the configured data table.

        Args:
            data: A dictionary containing telemetry data with the following required fields:
                - parcel_id: Unique identifier for the parcel (string, 1-50 chars)
                - device_id: Unique identifier for the IoT device (string, 1-100 chars)
                - temperature: Temperature reading in Celsius (-100.0 to 200.0)
                - tilt_x: Tilt angle on X-axis in degrees (-180.0 to 180.0)
                - tilt_y: Tilt angle on Y-axis in degrees (-180.0 to 180.0)
                - latitude: GPS latitude coordinate (-90.0 to 90.0)
                - longitude: GPS longitude coordinate (-180.0 to 180.0)

        Returns:
            TelemetryData: The validated telemetry data that was saved to the database.

        Raises:
            SaveTelemetryInvalidDataError: If the payload fails Pydantic validation.
            SaveTelemetryInvalidGpsDataError: If both latitude and longitude are 0.0.
        """
        if data is None:
            raise SaveTelemetryInvalidDataError()

        # Validate payload using Pydantic
        telemetry: Optional[TelemetryData] = None
        try:
            telemetry = TelemetryData(**data)
        except ValueError as e:
            raise SaveTelemetryInvalidDataError()

        # Validate GPS coordinates (not both zero)
        if not TelemetryIngestionService._validate_gps_coordinates(
            telemetry.latitude, telemetry.longitude
        ):
            raise SaveTelemetryInvalidGpsDataError()

        _ = self._data_table.save_telemetry(telemetry=telemetry)

        return telemetry

    def is_healthy(self) -> bool:
        """Check if the ingestion service is healthy.

        Verifies that the underlying data table connection is active and healthy.

        Returns:
            True if the data table is connected, False otherwise.
        """
        return self._data_table.is_connected()

    @staticmethod
    def _validate_gps_coordinates(latitude: float, longitude: float) -> bool:
        """Validate that GPS coordinates are not both zero (indicating un-locked GPS).

        Args:
            latitude: GPS latitude coordinate
            longitude: GPS longitude coordinate

        Returns:
            True if coordinates are valid, False if both are zero
        """
        return not (latitude == 0.0 and longitude == 0.0)
