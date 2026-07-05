# Python Ingest Service

Lightweight asynchronous Python ingestion microservice for the Parcel State Tracker Platform. This service handles high-throughput telemetry data ingestion from IoT edge devices, validates incoming payloads, and persists validated data to MongoDB.

## 🏗️ Architecture Role

This service serves as the entry point for all IoT telemetry data in the platform:

```
[ IoT Edge Devices ] → HTTP POST (JSON) → [ Python Ingest Service ] → [ MongoDB ]
                                                 ↓
                                          Flask (Port 5000)
                                          Pydantic Validation
```

## 🛠️ Tech Stack

- **Python** - Core language
- **Flask** - Lightweight web framework for HTTP API
- **Pydantic** - Data validation and settings management
- **PyMongo** - MongoDB Python driver
- **MongoDB** - NoSQL document database for telemetry storage

## 📋 Features

- **Asynchronous ingestion** of telemetry data from multiple IoT devices
- **Strict validation** using Pydantic schemas to ensure data integrity
- **Automatic timestamp** generation for all ingested records
- **GPS data validation** (rejects un-locked 0.0 coordinates)
- **High-throughput** design optimized for IoT data streams

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
  "document_id": "660c1d4f2b1a8c4d23e8f9a1"
}
```

**Stored Document in MongoDB:**
```json
{
  "_id": {"$oid": "660c1d4f2b1a8c4d23e8f9a1"},
  "parcel_id": "A1B2C3D4",
  "device_id": "STM32_NUCLEO_01",
  "temperature": 22.4,
  "tilt_x": 12.1,
  "tilt_y": -3.5,
  "latitude": 13.1394,
  "longitude": 122.7483,
  "timestamp": "2026-07-05T22:45:00.000Z"
}
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- MongoDB instance (local or remote)

### Installation

1. **Navigate to the service directory:**
```bash
cd service-ingest-python
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
```

3. **Activate the virtual environment:**
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Configure environment variables:**
Create a `.env` file in the root directory with:
```
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USERNAME=
MONGODB_PASSWORD=
MONGODB_DB_NAME=parcel_tracker
MONGODB_AUTH_SOURCE=admin
FLASK_ENV=development
FLASK_PORT=5000
```

6. **Run the service:**
```bash
python app.py
```

The service will start on `http://localhost:5000` (or the port specified in your environment).

### Docker Deployment

The service can be deployed as part of the complete platform using Docker Compose from the `deployment/` directory:

```bash
cd deployment
docker-compose up --build
```

This will start the Python ingest service along with MongoDB, the Java backend, and the React frontend.

## 🧪 Testing

### Manual Testing with cURL

Test the ingestion endpoint:
```bash
curl -X POST http://localhost:5000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "parcel_id": "X9Y8Z7W6",
    "device_id": "TEST_DEVICE_01",
    "temperature": 25.0,
    "tilt_x": 5.0,
    "tilt_y": -2.0,
    "latitude": 14.5995,
    "longitude": 120.9842
  }'
```

### Using Postman

1. Create a new POST request to `http://localhost:5000/api/v1/ingest`
2. Set the body type to `raw` and `JSON`
3. Use the sample payload from the API section above
4. Send the request and verify the response

## 📁 Project Structure

```
service-ingest-python/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment configuration (create from .env.example)
├── .env.example          # Example environment configuration
└── README.md             # This file
```

## 🔧 Configuration

The service is configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_HOST` | MongoDB server hostname | `localhost` |
| `MONGODB_PORT` | MongoDB server port | `27017` |
| `MONGODB_USERNAME` | MongoDB username (leave empty for no auth) | `` |
| `MONGODB_PASSWORD` | MongoDB password (leave empty for no auth) | `` |
| `MONGODB_DB_NAME` | Database name | `parcel_tracker` |
| `MONGODB_AUTH_SOURCE` | MongoDB authentication database | `admin` |
| `FLASK_ENV` | Flask environment (development/production) | `development` |
| `FLASK_PORT` | Port to run the service on | `5000` |

### 🔒 MongoDB Authentication Setup

To enable password protection for MongoDB:

1. **Create a MongoDB user** (run in MongoDB shell):
   ```javascript
   use admin
   db.createUser({
     user: "parcel_tracker_user",
     pwd: "your_secure_password_here",
     roles: [
       { role: "readWrite", db: "parcel_tracker" }
     ]
   })
   ```

2. **Enable authentication in MongoDB**:
   - If using Docker, set `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD` environment variables
   - Or modify MongoDB configuration to require authentication

3. **Configure the service** by updating your `.env` file:
   ```
   MONGODB_HOST=localhost
   MONGODB_PORT=27017
   MONGODB_USERNAME=parcel_tracker_user
   MONGODB_PASSWORD=your_secure_password_here
   MONGODB_DB_NAME=parcel_tracker
   MONGODB_AUTH_SOURCE=admin
   ```

4. **Restart the service** for changes to take effect.

> **Security Note**: Never commit your `.env` file to version control. The `.env.example` file is provided as a template with empty credentials.

## 🛡️ Validation Rules

The service enforces the following validation rules on incoming data:

1. **Required fields**: `parcel_id`, `device_id`, `temperature`, `tilt_x`, `tilt_y`, `latitude`, `longitude`
2. **Data types**: All numeric fields must be valid numbers
3. **GPS validation**: Rejects records with both latitude and longitude as 0.0 (un-locked GPS)
4. **Temperature range**: Validates temperature is within reasonable bounds
5. **Tilt angles**: Validates tilt values are within acceptable ranges

## 🐛 Error Handling

The service returns appropriate HTTP status codes:

- `200 OK` - Successful ingestion
- `400 Bad Request` - Invalid payload or validation failure
- `500 Internal Server Error` - Server-side errors

Error responses include detailed messages to help with debugging.

## 📈 Monitoring

The service logs all ingestion events to the console, including:
- Successful ingestions with document IDs
- Validation failures with reasons
- Database connection status
- Anomaly detections

## 🔗 Integration with Platform

This service integrates with other components of the Parcel State Tracker Platform:

- **Receives data from**: IoT edge devices (STM32 Nucleo boards with ESP8266 Wi-Fi)
- **Stores data in**: MongoDB (shared with Java Spring Boot backend)
- **Data consumed by**: Java Spring Boot REST API for serving to React dashboard

## 🤝 Contributing

When making changes to this service:

1. Ensure all validation rules are properly tested
2. Maintain backward compatibility with existing API contracts
3. Update this README with any new configuration options or endpoints
4. Follow the existing code structure and patterns

## 📄 License

This service is part of the Parcel State Tracker Platform and follows the same license as the root project.