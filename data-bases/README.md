# MongoDB Database Service

This directory contains the MongoDB database configuration for the Parcel State Tracker Platform.

## Overview

The MongoDB service provides the primary data storage for the platform with the following collections:

- **users** - Stores user names and passwords for authentication
- **deliveries** - Contains delivery information including tracking details

## Prerequisites

- Docker and Docker Compose installed on your system

## Quick Start

1. Copy the environment configuration file:

```bash
cp .env.docker.example .env.docker
```

2. Start the MongoDB service:

```bash
docker-compose up -d
```

3. The database will be available at `mongodb://localhost:27017` (or your configured port)
4. MongoDB Express admin interface will be available at `http://localhost:8081`

## Configuration

Environment variables can be configured in `.env.docker`:

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_USERNAME` | MongoDB admin username | `admin` |
| `MONGODB_PASSWORD` | MongoDB admin password | `admin123` |
| `MONGODB_DB_NAME` | Database name | `parcel_tracker` |
| `MONGODB_PORT` | MongoDB port | `27017` |
| `MONGO_EXPRESS_PORT` | MongoDB Express port | `8081` |
| `MONGO_EXPRESS_USERNAME` | MongoDB Express username | `admin` |
| `MONGO_EXPRESS_PASSWORD` | MongoDB Express password | `express123` |

## Collections Schema

### users Collection

```javascript
{
  _id: ObjectId,
  username: String,      // Unique username
  password: String,      // Hashed password (bcrypt recommended)
  email: String,         // Unique email address
  role: String,          // User role (admin, user)
  createdAt: Date,
  updatedAt: Date
}
```

### deliveries Collection

```javascript
{
  _id: ObjectId,
  trackingNumber: String,    // Unique tracking number
  senderName: String,
  senderAddress: String,
  recipientName: String,
  recipientAddress: String,
  status: String,            // Status: created, in_transit, delivered
  currentLocation: String,
  expectedDeliveryDate: Date,
  createdAt: Date,
  updatedAt: Date,
  trackingHistory: [{
    status: String,
    location: String,
    timestamp: Date
  }]
}
```

## Connecting to MongoDB

```bash
# Using mongosh
mongosh mongodb://localhost:27017/parcel_tracker

# Using connection string
mongodb://admin:admin123@localhost:27017/parcel_tracker?authSource=admin
```

## MongoDB Express Admin Interface

Access the web-based MongoDB admin interface at: `http://localhost:8081`

Login credentials:
- Username: `admin` (or `MONGO_EXPRESS_USERNAME` from .env.docker)
- Password: `express123` (or `MONGO_EXPRESS_PASSWORD` from .env.docker)

## Stopping the Service

```bash
docker-compose down
```

To also remove the data volume:

```bash
docker-compose down -v
```

## Directory Structure

```
data-bases/
├── docker-compose.yml      # MongoDB and MongoDB Express services
├── .env.docker.example   # Environment configuration template
└── .env.docker           # Your environment configuration (create from example)