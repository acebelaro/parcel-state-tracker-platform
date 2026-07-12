# Parcel State Tracker Platform

A firmware platform for tracking parcel state using temperature and tilt sensors, designed to transmit telemetry data over WiFi to a remote service.

## Summary

This project implements a telemetry system that monitors parcel conditions by reading temperature and tilt/angle data from sensors. The firmware connects to WiFi and periodically sends sensor readings to a configured ingest service. It supports multiple target boards through PlatformIO's multi-environment configuration.

### Features

- **Temperature Monitoring**: Reads temperature data from connected sensors
- **Tilt Detection**: Captures roll and pitch angles for orientation tracking
- **WiFi Connectivity**: Connects to configured WiFi networks for data transmission
- **Configurable Sampling**: Adjustable sensor sampling rate via configuration file
- **Multi-Target Support**: Works with Arduino and STM32 boards

## Configuration (app_config.yaml)

The application is configured via `app_config.yaml`. A sample template is provided in `app_config.yaml.sample`.

1. Copy `app_config.yaml.sample` to `app_config.yaml`:
   ```bash
   cp app_config.yaml.sample app_config.yaml
   ```

2. Edit `app_config.yaml` with your settings:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `COURIER_ID` | Identifier for the courier/service provider | `"ArduinoTestCourier"` |
| `DEVICE_ID` | Unique identifier for this device | `"ARDUINO_R4_UNO_WIFI"` |
| `WIFI_SSID` | WiFi network name |  |
| `WIFI_PASS` | WiFi network password |  |
| `SENSOR_SAMPLING_RATE_MS` | Sensor sampling interval in milliseconds | `5000` |
| `SERVICE_INGEST_TARGET_IP` | IP address of the ingest service |  |
| `SERVICE_INGEST_TARGET_PORT` | Port of the ingest service |  |

> **Note**: Add `app_config.yaml` to your `.gitignore` to keep credentials out of version control.

## Target Board

The firmware currently supports the following target boards:

### Primary Target: Arduino Uno R4 WiFi

- **Board**: Arduino Uno R4 WiFi (Renesas RA core)
- **Platform**: `renesas-ra`
- **Framework**: Arduino
- **Build Environment**: `env:arduino_r4`

### Alternative Target: STM32

- **Board**: Generic STM32F407VGT6 (configurable)
- **Platform**: `stm32`
- **Framework**: STM32Cube (HAL-based, no Arduino abstraction)
- **Build Environment**: `env:stm32_target`

## Build Using PlatformIO Extension

### Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/) with [PlatformIO IDE Extension](https://platformio.org/platformio-ide)
- Python 3.x (for configuration script)

### Build Commands

Using PlatformIO CLI:

```bash
# Build for Arduino Uno R4 WiFi
pio run -e arduino_r4

# Build for STM32 target
pio run -e stm32_target

# Upload to connected device
pio run -e arduino_r4 -t upload

# Monitor serial output
pio run -e arduino_r4 -t monitor
```

### Visual Studio Code

1. Open the project in VS Code
2. Install the PlatformIO IDE extension if not already installed
3. Select your target environment from the bottom status bar
4. Press **Ctrl+Alt+B** to build or **Ctrl+Alt+U** to build and upload

### How Configuration Works

The `load_config.py` script (specified in `extra_scripts`) automatically parses `app_config.yaml` during build and injects the configuration values as C++ preprocessor macros. This allows the firmware to access configuration values at compile time without hardcoding them.

## Project Structure

```
├── src/
│   └── main.cpp           # Main application entry point
├── inc/
│   ├── logger.hpp         # Logging utilities
│   ├── sensor.hpp         # Sensor base definitions
│   ├── sensorComms.hpp    # Sensor communication interface
│   ├── temperatureSensor.hpp
│   ├── tiltSensor.hpp
│   ├── time.hpp           # Time/clock utilities
│   └── wifiControl.hpp      # WiFi connectivity control
├── target/
│   ├── arduino/           # Arduino-specific implementations
│   ├── stm32/             # STM32-specific implementations
│   └── target.hpp         # Target abstraction header
├── platformio.ini         # PlatformIO build configuration
├── load_config.py         # Configuration injection script
└── app_config.yaml.sample   # Configuration template