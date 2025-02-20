#!/bin/bash
set -e

echo "Starting application..."
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

echo "Checking Python environment:"
which python
python --version
echo "PYTHONPATH: $PYTHONPATH"

echo "Checking for required files:"
echo "Checking /app/api/app.py..."
if [ ! -f "/app/api/app.py" ]; then
    echo "ERROR: /app/api/app.py not found!"
    ls -la /app/api/
    exit 1
fi

echo "Checking /app/api/templates..."
if [ ! -d "/app/api/templates" ]; then
    echo "ERROR: /app/api/templates directory not found!"
    ls -la /app/api/
    exit 1
fi

echo "Templates directory contents:"
ls -la /app/api/templates/

echo "Environment variables:"
echo "PORT: $PORT"
echo "FLASK_APP: $FLASK_APP"
echo "FLASK_ENV: $FLASK_ENV"

# Railway uses port 8080 internally
PORT=${PORT:-8080}
echo "Using port: $PORT"

# Start Flask API with gunicorn
echo "Starting gunicorn..."
cd /app/api
exec gunicorn \
    --bind "0.0.0.0:${PORT}" \
    --workers 1 \
    --log-level debug \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    app:app
