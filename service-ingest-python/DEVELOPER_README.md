# Developer Guide - Python Ingest Service

This guide provides detailed information for developers working on the Python Ingest Service, including testing procedures, project structure, and architectural details.

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
- **Ingest service tests** - Payload validation, GPS validation, and health checks
- **Exception tests** - Error message verification and inheritance
- **Boundary value tests** - Min/max value validation for telemetry fields

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
3. Use the sample payload from the API section in `README.md`
4. Send the request and verify the response

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
├── README.md             # User-facing documentation
├── DEVELOPER_README.md   # Developer guide (this file)
├── DEPLOYMENT_README.md  # Deployment guide
├── unit_tests/           # Unit test suite
│   ├── __init__.py       # Test package initialization
│   ├── test_mongo_data_table.py  # MongoDB data table unit tests
│   └── test_ingest_service.py    # Telemetry Ingestion Service unit tests
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
3. Update this DEVELOPER_README.md with any new development procedures
4. Update README.md with any user-facing changes
5. Update DEPLOYMENT_README.md with any deployment-related changes
6. Follow the existing code structure and patterns