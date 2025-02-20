# Build stage for Web
FROM node:18.17.0-slim as web-builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy web files
COPY web/ ./web/

# Build web
WORKDIR /app/web
RUN pnpm install
RUN pnpm run build

# Build stage for API
FROM python:3.12-slim-bookworm as api-builder

WORKDIR /app

# Copy API files
COPY api/ ./api/
COPY --from=web-builder /app/web/.next ./web/.next

# Install Python dependencies
WORKDIR /app/api
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Set environment variables
ENV FLASK_APP=app.py
ENV PORT=8000

# Start command
CMD cd /app/api && \
    gunicorn app:app --bind 0.0.0.0:$PORT --worker-class gevent
