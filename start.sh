#!/bin/bash
set -e

echo "Current directory: $(pwd)"
echo "Listing contents:"
ls -la

# Change to the API directory
cd /app/api || exit 1
echo "Changed to API directory: $(pwd)"
echo "API directory contents:"
ls -la

echo "Python version:"
python --version

echo "Checking for required files:"
if [ ! -f "app.py" ]; then
    echo "ERROR: app.py not found!"
    exit 1
fi

if [ ! -d "templates" ]; then
    echo "ERROR: templates directory not found!"
    exit 1
fi

echo "Templates directory contents:"
ls -la templates/

# Railway uses port 8080 internally
PORT=${PORT:-8080}
echo "Using port: $PORT"

# Start Flask API with gunicorn
echo "Starting gunicorn..."
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
