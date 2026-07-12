
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include "logger.hpp"
#include "tiltSensor.hpp"

// I2C Addresses
#define MPU_ADDR 0x68 // MPU-92.65 Address
static tSensorStatus tiltSensorStatus = SENSOR_STATUS_UNINITIALIZED;

void initializeTiltSensor(void)
{
    // 2. Wake up the MPU-92.65 Tilt Sensor over raw I2C
    Wire.beginTransmission(MPU_ADDR);
    Wire.write(0x6B); // Power Management 1 register
    Wire.write(0x00); // Set to 0 to wake it up
    byte mpuError = Wire.endTransmission();

    if (mpuError != 0)
    {
        LOG_ERROR("MPU-92.65 failed to respond at 0x68!");
        while (1)
            delay(10);
        tiltSensorStatus = SENSOR_STATUS_INITIALIZED_FAILED;
    }
    else
    {
        tiltSensorStatus = SENSOR_STATUS_INITIALIZED_SUCCESS;
    }
}

tSensorReading readTilt(tTiltReading *tiltReading)
{
    tSensorReading tiltReadingResult = SENSOR_READING_FAILED;
    // bool mpuDataReady = false;

    Wire.beginTransmission(MPU_ADDR);
    Wire.write(0x3B); // Starting register for Accelerometer Data
    Wire.endTransmission(false);
    Wire.requestFrom(MPU_ADDR, 6, true);

    if (Wire.available() >= 6)
    {
        int16_t rawX = (Wire.read() << 8) | Wire.read();
        int16_t rawY = (Wire.read() << 8) | Wire.read();
        int16_t rawZ = (Wire.read() << 8) | Wire.read();

        // Convert raw integers to G-forces (assuming standard +/-2G scale)
        float ax = rawX / 16384.0;
        float ay = rawY / 16384.0;
        float az = rawZ / 16384.0;

        // Trigonometry calculation for Pitch and Roll
        tiltReading->roll = atan2(ay, az) * 180.0 / M_PI;
        tiltReading->pitch = atan2(-ax, sqrt(ay * ay + az * az)) * 180.0 / M_PI;

        tiltReadingResult = SENSOR_READING_SUCCESS;
    }

    return tiltReadingResult;
}

tSensorStatus getTiltSensorStatus(void)
{
    return tiltSensorStatus;
}
