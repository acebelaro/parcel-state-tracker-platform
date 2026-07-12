#include "tiltSensor.hpp"

static tSensorStatus tiltSensorStatus = SENSOR_STATUS_UNINITIALIZED;

void initializeTiltSensor(void)
{
}

tSensorReading readTilt(tTiltReading *tiltReading)
{
}

tSensorStatus getTiltSensorStatus(void)
{
    return tiltSensorStatus;
}
