# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system packages required for building dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
 && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements .
RUN pip install --upgrade pip && pip install -r requirements

# Copy your application code
COPY . .

# By default, run the worker script (this can be overridden in docker-compose)
CMD ["python", "worker.py"]

