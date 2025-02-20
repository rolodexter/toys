# Build stage for Web
FROM node:18.17.0-slim as web-builder

WORKDIR /app/web

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    make \
    g++ \
    git \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm@latest

# Copy web files and install dependencies
COPY web/package.json web/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Copy and build web app
COPY web/ ./
RUN pnpm run build

# Production stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpq-dev \
    postgresql-server-dev-all \
    gcc \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy web build output
COPY --from=web-builder /app/web/.next/standalone ./
COPY --from=web-builder /app/web/.next/static ./.next/static
COPY --from=web-builder /app/web/public ./public

# Copy and install Python requirements
COPY api/requirements.txt ./api/
RUN pip install --no-cache-dir -r api/requirements.txt

# Copy API code and start script
COPY api/ ./api/
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Set environment variables
ENV PORT=3000
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

CMD ["/start.sh"]
