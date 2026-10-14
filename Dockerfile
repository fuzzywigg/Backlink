# Use official Python runtime as a parent image
FROM python:3.11-slim

# Non-secret build provenance (inject at build time; never put secrets here)
ARG GIT_SHA=unknown
ARG BUILD_ID=
ARG BUILD_TIMESTAMP=

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    GIT_SHA=${GIT_SHA} \
    BUILD_ID=${BUILD_ID} \
    BUILD_TIMESTAMP=${BUILD_TIMESTAMP}

# Set working directory
WORKDIR /app

# Install system dependencies (git is often needed for some pip packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories that might be excluded by .dockerignore but needed
RUN mkdir -p hive/honeycomb/logs

# Run the web service on container startup
CMD ["uvicorn", "hive.main_service:app", "--host", "0.0.0.0", "--port", "8080"]
