#include <Adafruit_BMP280.h>
#include "temperatureSensor.hpp"
#include "logger.hpp"

#define BMP_ADDR 0x76 // BMP280 Address

static tSensorStatus temperatureSensorStatus = SENSOR_STATUS_UNINITIALIZED;
static Adafruit_BMP280 *pBmpSensor = NULL;

void initializeTemperatureSensor(void)
{
    if (NULL == pBmpSensor)
    {
        pBmpSensor = new Adafruit_BMP280();
        if (pBmpSensor->begin(BMP_ADDR))
        {
            // Configure basic settings for the BMP280
            pBmpSensor->setSampling(Adafruit_BMP280::MODE_NORMAL,
                                    Adafruit_BMP280::SAMPLING_X2,
                                    Adafruit_BMP280::SAMPLING_X16,
                                    Adafruit_BMP280::FILTER_X16,
                                    Adafruit_BMP280::STANDBY_MS_500);
            temperatureSensorStatus = SENSOR_STATUS_INITIALIZED_SUCCESS;
        }
        else
        {
            temperatureSensorStatus = SENSOR_STATUS_INITIALIZED_FAILED;
            LOG_ERROR("Temperature initialization failed!");
        }
    }
    else
    {
        LOG_ERROR("Temperature Sensor Already initialized!");
    }
}

tSensorReading readTemperature(tTemperatureReading *temperatureReading)
{
    tSensorReading sensorReading = SENSOR_READING_FAILED;
    if (pBmpSensor && temperatureSensorStatus == SENSOR_STATUS_INITIALIZED_SUCCESS)
    {
        temperatureReading->temperatureCelcius = pBmpSensor->readTemperature();
        sensorReading = SENSOR_READING_SUCCESS;
    }
    else
    {
        temperatureReading->temperatureCelcius = 0.0;
    }
    return sensorReading;
}

tSensorStatus getTemperatureSensorStatus(void)
{
    return temperatureSensorStatus;
}
