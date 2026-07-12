#pragma once

#include "sensor.hpp"

typedef struct TiltReading
{
    float roll;
    float pitch;
} tTiltReading;

void initializeTiltSensor(void);
tSensorReading readTilt(tTiltReading *tiltReading);
tSensorStatus getTiltSensorStatus(void);
