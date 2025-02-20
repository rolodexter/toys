#!/bin/bash
set -e

# Change to the API directory
cd /app/api || exit 1
echo "Starting Flask API..."

# Railway uses port 8080 internally
PORT=${PORT:-8080}
echo "Using port: $PORT"

# Start Flask API with gunicorn
exec gunicorn \
    --bind "0.0.0.0:${PORT}" \
    --workers 1 \
    --log-level debug \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --preload \
    app:app
