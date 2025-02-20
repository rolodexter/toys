#!/bin/bash

# Enable error handling
set -e

echo "Starting Flask service..."
echo "PORT=$PORT"
echo "PWD=$(pwd)"

cd /app/api
if [ ! -f "app.py" ]; then
    echo "Error: app.py not found in /app/api"
    ls -la /app/api
    exit 1
fi

# Start Flask
gunicorn app:app \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --log-level debug \
    --error-logfile - \
    --access-logfile - \
    --capture-output
