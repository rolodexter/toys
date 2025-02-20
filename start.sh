#!/bin/bash

# Start Next.js
node server.js &

# Start Flask
cd api && gunicorn app:app --bind 0.0.0.0:$PORT --worker-class gevent
