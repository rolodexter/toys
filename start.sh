#!/bin/bash
set -e

cd /app/api
echo "Starting Flask API..."

# Get port from environment or default to 3000
export PORT=${PORT:-3000}
echo "Using port: $PORT"

# Start Flask API directly
exec python -u app.py
