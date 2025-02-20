#!/bin/bash
set -e

cd /app/api || exit 1
echo "Starting services..."

# Default to port 3000 if not set
export PORT=${PORT:-3000}

# Initialize database
echo "Initializing database..."
python -c "
from app import db
db.create_all()
"

# Start Flask API
echo "Starting Flask API on port $PORT..."
exec gunicorn app:app \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --log-level debug \
    --timeout 300 \
    --access-logfile - \
    --error-logfile -
