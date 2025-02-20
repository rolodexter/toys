# Stage 1: Build API
FROM python:3.12-slim-bookworm AS api-base

WORKDIR /app/api

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc g++ libc-dev libffi-dev libgmp-dev libmpfr-dev libmpc-dev \
    curl nodejs libgmp-dev libmpfr-dev libmpc-dev \
    expat libldap-2.5-0 perl libsqlite3-0 zlib1g \
    fonts-noto-cjk media-types libmagic1 \
    git make cmake pkg-config \
    libjpeg-dev libpng-dev libtiff-dev \
    libxml2-dev libxslt-dev \
    libssl-dev libffi-dev \
    postgresql postgresql-contrib libpq-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy Dify API files
COPY --from=langgenius/dify-api:0.15.3 /app /app/api

# Copy requirements file
COPY docker/requirements.txt /app/api/requirements.txt

# Set up Python environment and install dependencies
RUN python -m venv /app/api/venv && \
    . /app/api/venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Download NLTK data and set up tiktoken
RUN . /app/api/venv/bin/activate && \
    python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')" && \
    python -c "import tiktoken; tiktoken.encoding_for_model('gpt2')"

ENV TIKTOKEN_CACHE_DIR=/app/api/.tiktoken_cache

# Final stage
FROM python:3.12-slim-bookworm

WORKDIR /app/api

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl procps \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy the API files from the build stage
COPY --from=api-base /app/api /app/api

# Set environment variables
ENV FLASK_APP=app.py \
    EDITION=SELF_HOSTED \
    DEPLOY_ENV=PRODUCTION \
    CONSOLE_API_URL=http://127.0.0.1:5001 \
    CONSOLE_WEB_URL=http://127.0.0.1:3000 \
    SERVICE_API_URL=http://127.0.0.1:5001 \
    APP_WEB_URL=http://127.0.0.1:3000 \
    TZ=UTC \
    PYTHONPATH=/app/api \
    PATH="/app/api/venv/bin:$PATH" \
    FLASK_DEBUG=0 \
    FLASK_ENV=production \
    SECRET_KEY=your-secret-key \
    SQLALCHEMY_DATABASE_URI=sqlite:///db.sqlite \
    REDIS_HOST=localhost \
    REDIS_PORT=6379 \
    REDIS_DB=0 \
    REDIS_USERNAME="" \
    REDIS_PASSWORD="" \
    REDIS_USE_SSL=false \
    SESSION_TYPE=filesystem \
    SESSION_PERMANENT=true \
    SESSION_USE_SIGNER=true \
    OAUTH_REDIRECT_PATH=/console/api/oauth/authorize \
    OAUTH_REDIRECT_INDEX_PATH=/console/oauth/callback \
    CONSOLE_URL=http://127.0.0.1:3000 \
    API_URL=http://127.0.0.1:5001 \
    APP_URL=http://127.0.0.1:3000 \
    DEFAULT_LANG=en-US \
    CLEAN_UNFINISHED_INIT_MODEL_TASK=true

# Create a health check script
COPY <<EOF /healthcheck.sh
#!/bin/bash

echo "=== Starting health check ==="
echo "Date: $(date)"
echo "Hostname: $(hostname)"

# Show process status
echo "=== Process Status ==="
ps aux
echo "=== Memory Usage ==="
free -h || echo "free command not available"
echo "=== Disk Space ==="
df -h

# Check if the API is responding
echo "Checking API health..."
if ! curl -f http://localhost:5001/health; then
    echo "ERROR: API health check failed"
    echo "=== API Logs ==="
    tail -n 100 /app/api/gunicorn.log
    echo "=== Environment Variables ==="
    env
    exit 1
fi

echo "=== All health checks passed! ==="
exit 0
EOF

RUN chmod +x /healthcheck.sh

# Create required directories
RUN mkdir -p /app/api/instance /app/api/logs

# Expose API port
EXPOSE 5001

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=5 \
    CMD /healthcheck.sh

# Start the API server with the virtual environment
CMD ["/bin/bash", "-c", "source /app/api/venv/bin/activate && gunicorn -c gunicorn_config.py --log-file /app/api/gunicorn.log app:app"]
