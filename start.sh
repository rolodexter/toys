#!/bin/bash
set -e

cd /app/api
echo "Starting Flask API..."

# Get port from environment or default to 3000
PORT=${PORT:-3000}
echo "Using port: $PORT"

# Start Flask API
exec gunicorn app:app \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --log-level debug \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --capture-output
