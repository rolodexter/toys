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

# Set up Python environment and install dependencies
RUN python -m venv /app/api/venv && \
    . /app/api/venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install \
    flask==3.0.2 \
    flask-login==0.6.3 \
    flask-migrate==4.0.7 \
    flask-restful==0.3.10 \
    flask-sqlalchemy==3.1.1 \
    sqlalchemy==2.0.29 \
    psycopg2-binary==2.9.9 \
    redis==5.0.1 \
    celery==5.3.6 \
    gunicorn==21.2.0 \
    gevent==24.2.1 \
    authlib==1.3.0 \
    pyjwt==2.8.0 \
    cryptography==42.0.2 \
    python-dotenv==1.0.1 \
    openai==1.12.0 \
    tiktoken==0.6.0 \
    langchain==0.1.6 \
    langchain-openai==0.0.5 \
    langchain-community==0.0.19 \
    langfuse==2.51.5 \
    unstructured==0.12.3 \
    nltk==3.8.1 \
    numpy==1.26.4 \
    pandas==2.2.0 \
    beautifulsoup4==4.12.3 \
    python-magic==0.4.27 \
    pydantic==2.6.1 \
    pydantic-settings==2.1.0 \
    flask-compress==1.14 \
    flask-cors==4.0.0 \
    flask-limiter==3.5.0 \
    flask-session==0.6.0 \
    flask-smorest==0.42.3 \
    flask-socketio==5.3.6 \
    flask-wtf==1.2.1

# Download NLTK data and set up tiktoken
RUN . /app/api/venv/bin/activate && \
    python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')" && \
    python -c "import tiktoken; tiktoken.encoding_for_model('gpt2')"

ENV TIKTOKEN_CACHE_DIR=/app/api/.tiktoken_cache

# Stage 2: Build Web
FROM langgenius/dify-web:0.15.3 as web

# Stage 3: Final image
FROM nginx:alpine

# Install dependencies
RUN apk add --no-cache supervisor python3 py3-pip nodejs npm bash curl

# Copy the Dify API files
COPY --from=api-base /app/api /app/api
WORKDIR /app/api

# Copy the Dify web files
COPY --from=web /app /app/web
WORKDIR /app/web

# Copy nginx configuration
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf

# Create supervisor configuration
RUN mkdir -p /etc/supervisor/conf.d
COPY <<EOF /etc/supervisor/conf.d/supervisord.conf
[supervisord]
nodaemon=true
user=root
loglevel=debug

[program:api]
directory=/app/api
command=/app/api/venv/bin/gunicorn -c gunicorn_config.py app:app
environment=PYTHONPATH=/app/api
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
priority=1

[program:web]
directory=/app/web
command=npm start
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
priority=2

[program:nginx]
command=nginx -g 'daemon off;'
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
priority=3
EOF

# Create a health check script
COPY <<EOF /healthcheck.sh
#!/bin/bash
set -e

# Wait for services to be ready
sleep 10

# Check if supervisor is running
supervisorctl status all

# Check if the API is responding
curl -f http://localhost:5001/health || exit 1

# Check if the web interface is accessible
curl -f http://localhost:3000 || exit 1
EOF

RUN chmod +x /healthcheck.sh

# Set environment variables
ENV FLASK_APP=app.py
ENV EDITION=SELF_HOSTED
ENV DEPLOY_ENV=PRODUCTION
ENV CONSOLE_API_URL=http://127.0.0.1:5001
ENV CONSOLE_WEB_URL=http://127.0.0.1:3000
ENV SERVICE_API_URL=http://127.0.0.1:5001
ENV APP_WEB_URL=http://127.0.0.1:3000
ENV TZ=UTC
ENV PYTHONPATH=/app/api

# Expose ports
EXPOSE 80 5001 3000

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD /healthcheck.sh

# Start supervisor which will start all services
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
