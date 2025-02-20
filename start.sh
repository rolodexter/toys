#!/bin/bash
set -e

cd /app || exit 1
echo "Starting services..."

# Default to port 3000 if not set
export PORT=${PORT:-3000}
export FLASK_PORT=5000

# Start Flask API in background
cd /app/api
echo "Starting Flask API on port $FLASK_PORT..."
gunicorn app:app \
    --bind 0.0.0.0:$FLASK_PORT \
    --workers 1 \
    --log-level debug \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - &

# Wait for Flask to start
sleep 2

# Start Next.js
cd /app
echo "Starting Next.js on port $PORT..."
exec node server.js
