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

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- MongoDB instance (local or remote)
- Docker and Docker Compose (for containerized deployment)

### Local Installation

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

### Docker Deployment (Standalone)

Deploy the Python ingest service with MongoDB using Docker Compose:

1. **Navigate to the service directory:**
```bash
cd service-ingest-python
```

2. **Copy the Docker environment example:**
```bash
cp .env.docker.example .env.docker
```

3. **Customize environment variables (optional):**
Edit `.env.docker` to configure MongoDB credentials and other settings.

4. **Start the services:**
```bash
docker-compose up --build
```

This will:
- Build the Python ingest service container
- Start a MongoDB 7 container with persistent storage
- Start MongoDB Express for web-based database monitoring
- Configure networking between services
- Expose the service on port 5000 (or your configured port)
- Expose MongoDB Express on port 8081

5. **Verify the deployment:**
```bash
# Check service health
curl http://localhost:5000/api/v1/health

# View logs
docker-compose logs -f service-ingest-python
```

6. **Stop the services:**
```bash
docker-compose down
```

To remove all data and start fresh:
```bash
docker-compose down -v
```

### 📊 Monitoring MongoDB Data

The Docker deployment includes **MongoDB Express**, a web-based MongoDB admin interface:

**Access MongoDB Express:**
1. Open your browser and navigate to `http://localhost:8081`
2. Login with credentials from your `.env.docker` file:
   - Username: `admin` (or your configured `MONGO_EXPRESS_USERNAME`)
   - Password: `express123` (or your configured `MONGO_EXPRESS_PASSWORD`)

**What you can do with MongoDB Express:**
- View all databases and collections
- Browse and search documents in the `parcel_tracker` database
- View telemetry data ingested by the service (inside the `tracking` array)
- Execute queries and aggregations
- Import/export data
- Monitor database performance

**Alternative: Command-line monitoring**

You can also monitor MongoDB data using the MongoDB shell:

```bash
# Connect to MongoDB container
docker exec -it parcel-tracker-mongo mongosh -u admin -p admin123

# Switch to the parcel_tracker database
use parcel_tracker

# View all collections
show collections

# View all parcel documents
db.telemetry.find().pretty()

# Count total parcels
db.telemetry.countDocuments()

# View tracking entries for a specific parcel
db.telemetry.find({parcel_id: "A1B2C3D4"}).pretty()

# Get the latest tracking entry for a parcel
db.telemetry.find({parcel_id: "A1B2C3D4"}, {"tracking.0": 1, "parcel_id": 1})
```

### Full Platform Deployment

The service can also be deployed as part of the complete platform using Docker Compose from the `deployment/` directory:

```bash
cd deployment
docker-compose up --build
```

This will start the Python ingest service along with MongoDB, the Java backend, and the React frontend.

## 🧪 Testing

### Unit Tests

Run the unit tests for the MongoDB data table implementation:

```bash
# Navigate to the service directory
cd service-ingest-python

# Set Python path and run tests
set PYTHONPATH=.&& python -m pytest -v

# Or run with detailed output
set PYTHONPATH=.&& python -m pytest unit_tests/ -v --tb=short
```

The test suite includes:
- **Initialization tests** - Connection success and error handling
- **URI building tests** - Authentication configuration testing
- **Telemetry saving tests** - Document creation, updates, and error handling
- **Connection status tests** - MongoDB connectivity verification
- **Data validation tests** - Tracking entry structure validation

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
```

## 📁 Project Structure

```
service-ingest-python/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── pytest.ini             # Pytest configuration
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose configuration with MongoDB
├── .env                  # Environment configuration (create from .env.example)
├── .env.example          # Example environment configuration
├── .env.docker.example   # Example Docker deployment configuration
├── README.md             # This file
├── unit_tests/           # Unit test suite
│   ├── __init__.py       # Test package initialization
│   └── test_mongo_data_table.py  # MongoDB data table unit tests
└── service/               # Service package
    ├── __init__.py        # Service exports (exception classes)
    ├── ingest_service.py  # Core telemetry ingestion service
    └── data/              # Data abstraction layer
        ├── __init__.py    # Data module exports
        ├── data_table.py  # Abstract base class for database implementations
        ├── telemetry_data.py  # Pydantic model for telemetry validation
        └── mongo/         # MongoDB implementation
            ├── __init__.py  # MongoDB module exports
            └── mongo_data_table.py  # MongoDB DataTable implementation
```
```

## 🗄️ Database Abstraction Layer

The service uses a database-agnostic architecture that makes it easy to switch between different database backends or add support for new databases.

### Architecture Overview

The data layer follows the **Abstract Factory Pattern** with a clear separation between:

- **`DataTable`** (abstract base class) - Defines the interface for telemetry data storage
- **`MongoDataTable`** - MongoDB implementation of the `DataTable` interface
- **`TelemetryData`** - Pydantic model for data validation

This design allows for:
- **Easy database switching** - Instantiate a different `DataTable` implementation
- **Custom database support** - Create a new class implementing the `DataTable` interface
- **Testing flexibility** - Use mock implementations for unit tests
- **No code changes required** - The Flask app works with any `DataTable` implementation

### Adding Support for a New Database

To add support for a different database (e.g., PostgreSQL, MySQL, Redis):

1. **Create a new implementation** in `service/data/<database>/<database>_data_table.py`:
    ```python
    from ..data_table import DataTable, TelemetrySavingError
    from ..telemetry_data import TelemetryData
    
    class PostgresDataTable(DataTable):
        def __init__(self, max_tracking_entries: int = -1):
            super().__init__(max_tracking_entries=max_tracking_entries)
            # Initialize database connection
    
        def save_telemetry(self, telemetry: TelemetryData) -> str:
            # Implement save logic for PostgreSQL
            pass
    
        def is_connected(self) -> bool:
            # Implement connection check for PostgreSQL
            pass
    ```

2. **Update `app.py`** to use your implementation:
    ```python
    # Instead of:
    # from service.data.mongo.mongo_data_table import MongoDataTable
    
    # Use your new implementation:
    from service.data.<database>.<database>_data_table import <Database>DataTable
    
    def get_data_table() -> DataTable:
        global data_table
        if data_table is None:
            data_table = <Database>DataTable(max_tracking_entries=MAX_TRACKING_ENTRIES)
        return data_table
    ```

### DataTable Interface

All database implementations must extend the `DataTable` abstract base class and implement:

| Method | Description |
|--------|-------------|
| `save_telemetry(telemetry: TelemetryData) -> str` | Saves telemetry data and returns the document/parcel ID |
| `is_connected() -> bool` | Checks if the database connection is active |

### Built-in Implementations

| Class | Description | Location |
|-------|-------------|----------|
| `MongoDataTable` | MongoDB document storage with tracking array per parcel | `service/data/mongo/mongo_data_table.py` |

## ⚠️ Exception Classes

The service provides custom exception classes for handling telemetry ingestion errors:

| Exception | Description |
|-----------|-------------|
| `SaveTelemetryError` | Base exception for all telemetry saving failures |
| `SaveTelemetryInvalidDataError` | Raised when payload fails Pydantic validation (missing fields, invalid types, out-of-range values) |
| `SaveTelemetryInvalidGpsDataError` | Raised when GPS coordinates are both 0.0 (un-locked GPS) |

These exceptions can be imported from the service package:

```python
from service import SaveTelemetryError, SaveTelemetryInvalidDataError, SaveTelemetryInvalidGpsDataError

try:
    service.save_telemetry_data(data)
except SaveTelemetryInvalidDataError:
    # Handle validation errors
    pass
except SaveTelemetryInvalidGpsDataError:
    # Handle GPS lock errors
    pass
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