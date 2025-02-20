#!/bin/bash
set -e

echo "Current directory: $(pwd)"
echo "Listing contents:"
ls -la

# Change to the app directory
cd /app || exit 1
echo "Changed to app directory: $(pwd)"
echo "App directory contents:"
ls -la

echo "Python version:"
python --version

echo "Checking for required files:"
if [ ! -f "api/app.py" ]; then
    echo "ERROR: api/app.py not found!"
    exit 1
fi

if [ ! -d "api/templates" ]; then
    echo "ERROR: api/templates directory not found!"
    exit 1
fi

echo "Templates directory contents:"
ls -la api/templates/

# Railway uses port 8080 internally
PORT=${PORT:-8080}
echo "Using port: $PORT"

# Start Flask API with gunicorn
echo "Starting gunicorn..."
cd api
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
