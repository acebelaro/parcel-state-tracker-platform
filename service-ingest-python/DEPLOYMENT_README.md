# Deployment Guide - Python Ingest Service

This guide provides deployment-specific information for the Python Ingest Service, including local setup, Docker deployment, and configuration options.

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