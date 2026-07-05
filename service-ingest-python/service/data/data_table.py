"""
Data Table Abstraction

This module provides abstract base class and exception classes for telemetry data storage.
Subclasses should implement the DataTable interface for specific storage backends.
"""

from abc import ABC, abstractmethod
from .telemetry_data import TelemetryData


class TelemetryTableCreationError(Exception):
    """Exception raised when a telemetry data table cannot be created.
    
    Args:
        error: The error message describing why table creation failed.
    """

    def __init__(self, error: str):
        super().__init__(f"Failed to create telemetry table due to error: {error}")


class TelemetrySavingError(Exception):
    """Exception raised when telemetry data cannot be saved to the table.
    
    Args:
        error: The error message describing why the save operation failed.
    """

    def __init__(self, error: str):
        super().__init__(f"Failed to save telemetry data due to error: {error}")


class DataTable(ABC):
    """Abstract base class for a table to save parcel telemetry data.
    
    This class defines the interface for telemetry data storage implementations.
    Subclasses must implement the save_telemetry and is_connected methods.
    
    Args:
        max_tracking_entries: Maximum number of tracking entries to keep per parcel.
            Use -1 for unlimited entries. Defaults to -1.
    
    Attributes:
        _max_tracking_entries: Maximum number of tracking entries per parcel.
    """

    def __init__(
        self,
        max_tracking_entries: int = -1,
    ):
        super().__init__()
        self._max_tracking_entries = max_tracking_entries

    @abstractmethod
    def save_telemetry(self, telemetry: TelemetryData) -> str:
        """Saves the telemetry data to the table.
        
        Args:
            telemetry: The telemetry data to save.
            
        Returns:
            The parcel ID associated with the saved telemetry data.
            
        Raises:
            TelemetrySavingError: If the save operation fails.
        """
        raise NotImplementedError()

    @abstractmethod
    def is_connected(self) -> bool:
        """Checks if the connection to the data table is active.
        
        Returns:
            True if the connection is active, False otherwise.
        """
        raise NotImplementedError()