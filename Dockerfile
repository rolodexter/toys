# Build stage for Web
FROM node:18.17.0 as web-builder

WORKDIR /app/web

# Install dependencies
COPY web/package.json web/pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# Copy web files and build
COPY web/ ./
RUN pnpm run build

# Production stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy web build output
COPY --from=web-builder /app/web/.next/standalone ./
COPY --from=web-builder /app/web/.next/static ./.next/static
COPY --from=web-builder /app/web/public ./public

# Copy API files
COPY api/requirements.txt ./api/
WORKDIR /app/api
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy rest of API files
COPY api/ ./

# Set environment variables
ENV NODE_ENV=production
ENV PORT=8000
ENV HOSTNAME=0.0.0.0

# Start command
CMD cd /app/api && \
    gunicorn app:app --bind 0.0.0.0:$PORT --worker-class gevent
