#!/bin/bash
set -e

cd /app/api || exit 1
echo "Starting Flask on port $PORT"

# Default to port 3000 if not set
export PORT=${PORT:-3000}

exec gunicorn app:app \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --log-level debug \
    --timeout 300 \
    --access-logfile - \
    --error-logfile -
