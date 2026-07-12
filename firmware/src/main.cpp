
#include "target.hpp"
#include "logger.hpp"
#include "time.hpp"
#include "sensorComms.hpp"
#include "temperatureSensor.hpp"
#include "tiltSensor.hpp"
#include "wifiControl.hpp"

void setup()
{
  initializeLogging();

  LOG_INFO("=======================================");
  LOG_INFO("   Parcel Telemetry Application        ");
  LOG_INFO("=======================================");

  initializeWifi();

  initializeSensorComms();
  initializeTemperatureSensor();
  initializeTiltSensor();
}

tTemperatureReading temperatureReading;
tTiltReading tiltReading;

void loop()
{
  tSensorReading temperatureReadingResult = readTemperature(&temperatureReading);
  if (SENSOR_READING_SUCCESS == temperatureReadingResult)
  {
    LOG_INFO("Temperature: %.2f", temperatureReading.temperatureCelcius);
  }
  else
  {
    LOG_ERROR("Temperature reading error!");
  }

  tSensorReading tiltReadingResult = readTilt(&tiltReading);
  if (tiltReadingResult == SENSOR_READING_SUCCESS)
  {
    LOG_INFO("Roll: %.2f, Pitch: %.2f", tiltReading.roll, tiltReading.pitch);
  }
  else
  {
    LOG_ERROR("Tilt reading error!");
  }

  if (WIFI_STATUS_CONNECTED == getWifiStatus() &&
      SENSOR_READING_SUCCESS == temperatureReadingResult &&
      SENSOR_READING_SUCCESS == tiltReadingResult)
  {
    sendData(temperatureReading.temperatureCelcius, tiltReading.roll, tiltReading.pitch);
  }

  sleepMilliseconds(SENSOR_SAMPLING_RATE_MS);
}
