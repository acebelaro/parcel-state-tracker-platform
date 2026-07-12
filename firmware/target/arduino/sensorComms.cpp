#include "sensorComms.hpp"
#include "logger.hpp"
#include <Wire.h>

void initializeSensorComms(void)
{
    Wire.begin();
}