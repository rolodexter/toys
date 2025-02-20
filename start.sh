#!/bin/bash
set -e

cd /app/api || exit 1
echo "Starting Flask on port $PORT"
exec python app.py
