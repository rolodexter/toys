# Build stage for Web
FROM node:18.17.0-slim as web-builder

WORKDIR /app/web

# Set build environment variables
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV HUSKY=0

# Install build dependencies and clean up in same layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 make g++ && \
    npm install -g pnpm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY web/package.json web/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile --ignore-scripts

# Copy web files and build
COPY web/ ./
RUN pnpm run build

# Production stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Install system dependencies and clean up in same layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy web build output
COPY --from=web-builder /app/web/.next/standalone ./
COPY --from=web-builder /app/web/.next/static ./.next/static
COPY --from=web-builder /app/web/public ./public

# Copy API requirements and install Python packages
COPY api/requirements.txt ./api/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r api/requirements.txt

# Copy API files
COPY api/ ./api/

# Set environment variables
ENV PORT=8000
ENV FLASK_APP=api/app.py
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Copy start script and make it executable
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose port
EXPOSE 8000

CMD ["/start.sh"]
