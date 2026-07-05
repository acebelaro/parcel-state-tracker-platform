# Python Ingest Service

Lightweight asynchronous Python ingestion microservice for the Parcel State Tracker Platform. This service handles high-throughput telemetry data ingestion from IoT edge devices, validates incoming payloads, and persists validated data using a database-agnostic architecture.

## 🏗️ Architecture Role

This service serves as the entry point for all IoT telemetry data in the platform:

```
[ IoT Edge Devices ] → HTTP POST (JSON) → [ Python Ingest Service ] → [ Database ]
                                             ↓
                                        Flask (Port 5000)
                                        Pydantic Validation
```

## 🛠️ Tech Stack

- **Python** - Core language
- **Flask** - Lightweight web framework for HTTP API
- **Pydantic** - Data validation and settings management
- **PyMongo** - MongoDB Python driver (default implementation)

## 📋 Features

- **Asynchronous ingestion** of telemetry data from multiple IoT devices
- **Strict validation** using Pydantic schemas to ensure data integrity
- **Automatic timestamp** generation for all ingested records
- **GPS data validation** (rejects un-locked 0.0 coordinates)
- **High-throughput** design optimized for IoT data streams
- **Last 10 telemetry logs tracking:** MongoDB maintains only the most recent 10 telemetry records per parcel, automatically purging older entries to optimize storage and ensure fresh data visibility.

## 📡 API Endpoint

### POST `/api/v1/ingest`

Ingests telemetry data from IoT edge devices.

**Request Body:**
```json
{
  "parcel_id": "A1B2C3D4",
  "device_id": "STM32_NUCLEO_01",
  "temperature": 22.4,
  "tilt_x": 12.1,
  "tilt_y": -3.5,
  "latitude": 13.1394,
  "longitude": 122.7483
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Telemetry data ingested successfully",
  "parcel_id": "A1B2C3D4"
}
```

**Stored Document in MongoDB (per parcel):**
```json
{
  "_id": {"$oid": "660c1d4f2b1a8c4d23e8f9a1"},
  "parcel_id": "A1B2C3D4",
  "tracking": [
    {
      "temperature": 22.4,
      "tilt_x": 12.1,
      "tilt_y": -3.5,
      "latitude": 13.1394,
      "longitude": 122.7483,
      "timestamp": "2026-07-05T22:45:00.000Z"
    }
  ]
}
```

## 🔗 Integration with Platform

This service integrates with other components of the Parcel State Tracker Platform:

- **Receives data from**: IoT edge devices (STM32 Nucleo boards with ESP8266 Wi-Fi)
- **Stores data in**: MongoDB (shared with Java Spring Boot backend)
- **Data consumed by**: Java Spring Boot REST API for serving to React dashboard

## 📄 Getting Started

For deployment and setup instructions, see **[Deployment Guide](DEPLOYMENT_README.md)**.

For development guidelines, testing procedures, and architectural details, see **[Developer Guide](DEVELOPER_README.md)**.

For quick reference:
- See deployment guide in **[Deployment Guide](DEPLOYMENT_README.md)**
- Run `docker-compose up --build` for containerized deployment

## 📄 License

This service is part of the Parcel State Tracker Platform and follows the same license as the root project.