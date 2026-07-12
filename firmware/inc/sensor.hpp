#pragma once

typedef enum
{
    SENSOR_STATUS_UNINITIALIZED,
    SENSOR_STATUS_INITIALIZED_SUCCESS,
    SENSOR_STATUS_INITIALIZED_FAILED
} tSensorStatus;

typedef enum
{
    SENSOR_READING_FAILED,
    SENSOR_READING_SUCCESS
} tSensorReading;