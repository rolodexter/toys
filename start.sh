#!/bin/bash

# Enable error handling and logging
set -e
exec 1> >(logger -s -t $(basename $0)) 2>&1

echo "Starting services..."
echo "Environment check..."
echo "PORT=$PORT"
echo "FLASK_APP=$FLASK_APP"
echo "NODE_ENV=$NODE_ENV"
echo "PWD=$(pwd)"
echo "Contents of /app:"
ls -la /app
echo "Contents of /app/api:"
ls -la /app/api

# Calculate ports
NEXT_PORT=$PORT
FLASK_PORT=5000

# Start Next.js
echo "Starting Next.js on port $NEXT_PORT..."
cd /app
if [ ! -f "server.js" ]; then
    echo "Error: server.js not found in /app"
    ls -la /app
    exit 1
fi

export PORT=$NEXT_PORT
node server.js &
NEXT_PID=$!
echo "Next.js started with PID $NEXT_PID"

# Wait a moment to ensure Next.js is starting
sleep 2
if ! kill -0 $NEXT_PID 2>/dev/null; then
    echo "Error: Next.js failed to start"
    exit 1
fi

# Start Flask
echo "Starting Flask on port $FLASK_PORT..."
cd /app/api
if [ ! -f "app.py" ]; then
    echo "Error: app.py not found in /app/api"
    ls -la /app/api
    exit 1
fi

# Check if required environment variables are set
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL is not set"
    exit 1
fi
if [ -z "$REDIS_URL" ]; then
    echo "Error: REDIS_URL is not set"
    exit 1
fi

export PORT=$FLASK_PORT
export FLASK_ENV=production
export FLASK_DEBUG=0

gunicorn app:app \
    --bind 0.0.0.0:$FLASK_PORT \
    --worker-class gevent \
    --workers 2 \
    --timeout 120 \
    --log-level debug \
    --error-logfile - \
    --access-logfile - \
    --capture-output &
FLASK_PID=$!
echo "Flask started with PID $FLASK_PID"

# Wait a moment to ensure Flask is starting
sleep 2
if ! kill -0 $FLASK_PID 2>/dev/null; then
    echo "Error: Flask failed to start"
    exit 1
fi

# Handle shutdown
trap 'echo "Shutting down..."; kill $NEXT_PID $FLASK_PID' SIGTERM

# Monitor processes and check health
while true; do
    # Check Next.js
    if ! kill -0 $NEXT_PID 2>/dev/null; then
        echo "Next.js process died"
        exit 1
    fi
    
    # Check Flask
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "Flask process died"
        exit 1
    fi
    
    # Check if services are responding
    echo "Checking Next.js health..."
    if ! curl -s http://localhost:$NEXT_PORT/_next/static 2>/dev/null; then
        echo "Warning: Next.js not responding"
    fi
    
    echo "Checking Flask health..."
    if ! curl -s http://localhost:$FLASK_PORT/health 2>/dev/null; then
        echo "Warning: Flask not responding"
    fi
    
    sleep 5
done
