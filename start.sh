#!/bin/bash

# Start Next.js
cd /app && node server.js &
NEXT_PID=$!

# Start Flask
cd /app/api && gunicorn app:app --bind 0.0.0.0:$PORT --worker-class gevent &
FLASK_PID=$!

# Handle shutdown
trap 'kill $NEXT_PID $FLASK_PID' SIGTERM

# Wait for either process to exit
wait $NEXT_PID $FLASK_PID
