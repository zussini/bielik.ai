#!/bin/bash
# setup.sh
# This script sets up your environment by:
#   1. Updating system packages
#   2. Installing RabbitMQ (if needed) and starting its service via systemctl
#   3. Creating a Python virtual environment and installing required Python packages
#   4. Starting the worker and publisher scripts in the background
#
# NOTE: This example is written for Ubuntu/Debian.
# To use Docker instead, comment out the system-level commands and use the docker-compose files below.

set -e  # Exit immediately if a command fails

echo "Updating system packages..."
sudo apt-get update

# --- RabbitMQ Installation (Direct Host) ---
if ! command -v rabbitmqctl &>/dev/null; then
    echo "RabbitMQ not found. Installing RabbitMQ server..."
    sudo apt-get install -y rabbitmq-server
else
    echo "RabbitMQ already installed."
fi

echo "Starting RabbitMQ service..."
# Uncomment the next two lines if you want to use systemctl (for direct host installation)
#sudo systemctl start rabbitmq-server
#sudo systemctl enable rabbitmq-server

echo "RabbitMQ management console available at http://localhost:15672 (default credentials: guest/guest)"

# --- Python Environment Setup ---
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python dependencies..."
pip install pika vllm torch transformers
# (Add any additional dependencies as needed)

# --- Start Application Services ---
# It is assumed you have worker.py and publisher.py in your project directory.
echo "Starting worker..."
#nohup python worker.py > worker.log 2>&1 &
echo "Worker started (see worker.log for output)."

echo "Starting publisher..."
#nohup python publisher.py > publisher.log 2>&1 &
echo "Publisher started (see publisher.log for output)."

echo "Direct host setup complete."

