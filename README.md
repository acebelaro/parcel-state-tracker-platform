# Parcel State Tracker Platform

An enterprise-grade, polyglot IoT tracking platform designed to monitor the state of shipping parcels in real time. The system captures environmental metrics (temperature) and spatial orientations (tilt angles) alongside GPS geographic data using an edge microcontroller, streams the telemetry through a high-throughput Python ingestion microservice into a local MongoDB instance, and serves the data through an enterprise Java Spring Boot REST API to a live React JS dashboard.

---

## 🏗️ System Architecture


```

                            [ LOCAL NETWORK / Wi-Fi ]
                                       │
                                       ▼ HTTP POST (JSON)
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           LOCAL SYSTEM ENVIRONMENT                               │
│                                                                                  │
│   ┌─────────────────────────────┐                  ┌─────────────────────────┐   │
│   │    Python Ingest Service    │─────────────────>│      Local MongoDB      │   │
│   │        (Flask / Port 5000)  │                  │     (Telemetry Logs)    │   │
│   └─────────────────────────────┘                  └────────────┬────────────┘   │
│                                                                 │                │
│   ┌─────────────────────────────┐                               │                │
│   │   Java Spring Boot Backend  │<──────────────────────────────┘                │
│   │      (Enterprise API / 8080)│                                                │
│   └──────────────┬──────────────┘                                                │
└──────────────────┼───────────────────────────────────────────────────────────────┘
                   │
                   │ REST API / JSON
                   ▼
┌─────────────────────────────┐
│     React JS Dashboard      │
│  (Interactive Maps/Charts)  │
└─────────────────────────────┘

```

---

## 📁 Repository Structure

The project is managed as a unified monorepo to enable atomic feature commits and streamlined local orchestration profiles:

* **`📂 firmware/`**: Embedded software assets grouped by development target boards.
    * `📂 stm32-nucleo/`: Core operational firmware compiled in C utilizing HAL libraries and DMA ring buffers.
    * `📂 arduino-uno/`: Future architecture abstraction layer for Arduino prototyping modules.
* **`📂 service-ingest-python/`**: Lightweight asynchronous Python ingestion tool leveraging Flask and Pydantic validation rules.
* **`📂 backend-spring-boot/`**: Enterprise-tier Java application acting as the single source of truth for database aggregation and UI consumption.
* **`📂 frontend-react/`**: Single Page Application (SPA) tracking panel housing chart timelines and leaf maps.
* **`📂 data-bases/`**: MongoDB database service configuration with Docker Compose, including MongoDB Express admin interface for database management.

---

## 🛠️ Tech Stack & Components

### Hardware Component Specifications
* **Microcontroller:** STMicroelectronics `NUCLEO-F411RE` (ARM Cortex-M4 @ 100MHz)
* **Wi-Fi Modem:** Espressif `ESP-01 / ESP8266` Serial Transceiver
* **Geospatial Tracking:** u-blox `NEO-6M GPS Receiver` with Active Ceramic Patch Antenna
* **Inertial Measurement Unit:** `MPU-6050` 3-Axis Gyroscope & 3-Axis Accelerometer
* **Thermal Monitoring:** Maxim Integrated `DS18B20` Waterproof One-Wire Digital Probe

### Software Engineering Ecosystem
* **Firmware Layer:** C language, STM32CubeIDE Toolchain, HAL Architecture, Hardware Interrupts, and DMA.
* **Ingestion Pipeline:** Python, Flask, Pydantic, PyMongo.
* **Data Store:** MongoDB (NoSQL Document System natively holding BSON telemetry objects).
* **Enterprise Middleware:** Java 17, Spring Boot, Spring Data MongoDB.
* **Presentation Layer:** React JS, Tailwind CSS, Chart.js, React-Leaflet Maps.
* **DevOps & Deployment:** Docker, Docker Compose local runtime containerization.

---

## 🛰️ Telemetry API Data Payload

The hardware edge device maps sensor values directly to a unified JSON data package when transmitting telemetry payloads to the Python ingestion microservice:

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

The Python framework validates formatting bounds, enforces criteria schemas (e.g., rejecting un-locked `0.0` GPS data), generates a local server timestamp, and logs the document directly into MongoDB:

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

---

## 🚀 Quick Start Local Environment Integration

The entire platform ecosystem (excluding the physical microcontroller board) can be spun up locally inside Docker containers using the orchestrations found in the `data-bases/` directory.

### Prerequisites

* Docker Desktop installed on your system
* Postman (for mocking API calls)

### Execution Pipeline

1. **Clone the Repository:**
```bash
git clone [https://github.com/yourusername/parcel-state-tracker-platform.git](https://github.com/yourusername/parcel-state-tracker-platform.git)
cd parcel-state-tracker-platform

```

2. **Create the shared Docker network:**
```bash
docker network create parcel-tracker-network
```

3. **Start the Database Services:**
```bash
cd data-bases
cp .env.docker.example .env.docker
docker-compose up -d
```

4. **Start other services (optional):**
```bash
cd service-ingest-python
cp .env.docker.example .env.docker
docker-compose up -d
```

5. **Verify Database Services:**
* **MongoDB Engine** will be available on `localhost:27017`
* **MongoDB Express Admin Interface** will be available on `localhost:8081`


6. **Verify and Test Ingestion:**
Send an HTTP POST using Postman to the endpoint: `http://localhost:5000/api/v1/ingest` using the sample payload provided in the Telemetry section. Check your terminal logs to watch the ingestion pipeline and database engine seamlessly execute!

---

## 📈 Key Engineering Principles Demonstrated

* **Polyglot Microservices:** Separates high-frequency network input operations (Python/Flask) from enterprise query consolidation logic (Java/Spring Boot).
* **Low-Level Hardware Device Manipulation:** Writing robust drivers in C to directly decode register structures over I2C and UART buses.
* **Asynchronous Database Decoupling:** Isolates application services using MongoDB as a persistent document bridge, keeping individual services resilient to network connection drops.
* **Failsafe Telemetry Data Integrity:** Using strict runtime validation techniques (Pydantic) to catch data corruption before records reach production systems.
* **Last 10 Telemetry Logs:** MongoDB maintains only the most recent 10 telemetry records per parcel, automatically purging older entries to optimize storage and ensure fresh data visibility.
