# Python Ingest Service Docker Image
# Parcel State Tracker Platform

# Use lightweight Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY data/ ./data/

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]