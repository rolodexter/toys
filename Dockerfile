# Build stage for Web
FROM node:18.17.0-slim as web-builder

WORKDIR /app/web

# Set build environment variables
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV HUSKY=0
ENV HUSKY_SKIP_INSTALL=1
ENV NEXT_SHARP_PATH=/tmp/node_modules/sharp

# Install build dependencies and clean up in same layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    make \
    g++ \
    git \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm globally
RUN npm install -g pnpm@latest

# Install dependencies
COPY web/package.json web/pnpm-lock.yaml ./
RUN pnpm config set enable-pre-post-scripts false && \
    pnpm config set ignore-scripts true && \
    pnpm install --frozen-lockfile --prod && \
    pnpm install -D sharp esbuild && \
    pnpm rebuild sharp

# Copy web files and build
COPY web/ ./
RUN pnpm run build

# Production stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Set environment variables for PostgreSQL
ENV PATH="/usr/lib/postgresql/16/bin:${PATH}" \
    PG_MAJOR=16

# Install system dependencies and clean up in same layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    postgresql-server-dev-${PG_MAJOR} \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    gcc \
    g++ \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    # Verify pg_config is available
    pg_config --version

# Copy web build output
COPY --from=web-builder /app/web/.next/standalone ./
COPY --from=web-builder /app/web/.next/static ./.next/static
COPY --from=web-builder /app/web/public ./public

# Copy API requirements and install Python packages
COPY api/requirements.txt ./api/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel setuptools && \
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
