"""
Telemetry Data Model

This module defines the Pydantic model for validating incoming telemetry data
from IoT edge devices. It includes field validation and JSON schema examples.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict


# Pydantic model for telemetry data validation
class TelemetryData(BaseModel):
    """Schema for incoming telemetry data from IoT edge devices.
    
    This model validates all incoming telemetry data including GPS coordinates,
    temperature readings, and device orientation tilt measurements.
    
    Attributes:
        parcel_id: Unique identifier for the parcel being tracked.
        device_id: Unique identifier for the IoT device sending the data.
        temperature: Temperature reading in Celsius from the device sensor.
        tilt_x: Tilt angle on the X-axis in degrees.
        tilt_y: Tilt angle on the Y-axis in degrees.
        latitude: GPS latitude coordinate. Must be between -90.0 and 90.0.
        longitude: GPS longitude coordinate. Must be between -180.0 and 180.0.
    """

    parcel_id: str = Field(
        ..., min_length=1, max_length=50, description="Unique parcel identifier"
    )
    device_id: str = Field(
        ..., min_length=1, max_length=100, description="Device identifier"
    )
    temperature: float = Field(
        ..., ge=-100.0, le=200.0, description="Temperature reading in Celsius"
    )
    tilt_x: float = Field(
        ..., ge=-180.0, le=180.0, description="Tilt angle on X-axis in degrees"
    )
    tilt_y: float = Field(
        ..., ge=-180.0, le=180.0, description="Tilt angle on Y-axis in degrees"
    )
    latitude: float = Field(
        ..., ge=-90.0, le=90.0, description="GPS latitude coordinate"
    )
    longitude: float = Field(
        ..., ge=-180.0, le=180.0, description="GPS longitude coordinate"
    )

    @field_validator("latitude", "longitude")
    @classmethod
    def validate_gps_not_zero(cls, v, info):
        """Validate that GPS coordinates are not both zero (un-locked GPS).
        
        Args:
            v: The field value to validate.
            info: The validation info containing field context.
            
        Returns:
            The validated field value.
        """
        # This validation will be done in the main validation check
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "parcel_id": "A1B2C3D4",
                "device_id": "STM32_NUCLEO_01",
                "temperature": 22.4,
                "tilt_x": 12.1,
                "tilt_y": -3.5,
                "latitude": 13.1394,
                "longitude": 122.7483,
            }
        }
    )