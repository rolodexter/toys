#!/bin/bash
set -e

cd /app || exit 1
echo "Starting services..."

# Default to port 3000 if not set
export PORT=${PORT:-3000}

# Initialize database
cd /app/api
echo "Initializing database..."
python -c "
from app import db
db.create_all()
"

# Start Flask in background
echo "Starting Flask API..."
gunicorn app:app \
    --bind 127.0.0.1:5000 \
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
export NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:5000
exec node .next/standalone/server.js
