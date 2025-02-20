#!/bin/bash

# Enable error handling and logging
set -e
exec 1> >(logger -s -t $(basename $0)) 2>&1

echo "Starting services..."
echo "Environment: PORT=$PORT, FLASK_APP=$FLASK_APP"

# Start Next.js
echo "Starting Next.js..."
cd /app
if [ ! -f "server.js" ]; then
    echo "Error: server.js not found in /app"
    ls -la /app
    exit 1
fi
node server.js &
NEXT_PID=$!
echo "Next.js started with PID $NEXT_PID"

# Start Flask
echo "Starting Flask..."
cd /app/api
if [ ! -f "app.py" ]; then
    echo "Error: app.py not found in /app/api"
    ls -la /app/api
    exit 1
fi
gunicorn app:app --bind 0.0.0.0:$PORT --worker-class gevent --log-level debug &
FLASK_PID=$!
echo "Flask started with PID $FLASK_PID"

# Handle shutdown
trap 'echo "Shutting down..."; kill $NEXT_PID $FLASK_PID' SIGTERM

# Monitor processes
while true; do
    ps aux | grep $NEXT_PID | grep -q -v grep
    NEXT_STATUS=$?
    ps aux | grep $FLASK_PID | grep -q -v grep
    FLASK_STATUS=$?
    
    if [ $NEXT_STATUS -ne 0 ]; then
        echo "Next.js process died"
        exit 1
    fi
    if [ $FLASK_STATUS -ne 0 ]; then
        echo "Flask process died"
        exit 1
    fi
    
    sleep 5
done
