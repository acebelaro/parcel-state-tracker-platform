#pragma once

#include "sensor.hpp"

typedef struct TemperatureReading
{
    float temperatureCelcius;
} tTemperatureReading;

void initializeTemperatureSensor(void);
tSensorReading readTemperature(tTemperatureReading *temperatureReading);
tSensorStatus getTemperatureSensorStatus(void);
