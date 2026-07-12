#include "temperatureSensor.hpp"
#include "logger.hpp"

static tSensorStatus temperatureSensorStatus = SENSOR_STATUS_UNINITIALIZED;

void initializeTemperatureSensor(void)
{
    // TODO:
}

tSensorReading readTemperature(tTemperatureReading *temperatureReading)
{
    // TODO:
}

tSensorStatus getTemperatureSensorStatus(void)
{
    return temperatureSensorStatus;
}
