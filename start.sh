#!/bin/bash
set -e

cd /app/api || exit 1
echo "Starting Flask on port $PORT"
exec gunicorn app:app --bind 0.0.0.0:$PORT --log-level debug
