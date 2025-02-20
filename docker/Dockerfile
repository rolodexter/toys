# base image
FROM python:3.12-slim-bookworm AS base

WORKDIR /app/api

# Install Poetry
ENV POETRY_VERSION=2.0.1
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Configure Poetry
ENV POETRY_CACHE_DIR=/tmp/poetry_cache
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_VIRTUALENVS_CREATE=true
ENV POETRY_REQUESTS_TIMEOUT=15

FROM base AS packages

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ libc-dev libffi-dev libgmp-dev libmpfr-dev libmpc-dev

# Copy Dify API files and install dependencies
COPY --from=langgenius/dify-api:0.15.3 /app /app/api
RUN cd /app/api && poetry install --sync --no-cache --no-root

# production stage
FROM base AS production

ENV FLASK_APP=app.py
ENV EDITION=SELF_HOSTED
ENV DEPLOY_ENV=PRODUCTION
ENV CONSOLE_API_URL=http://127.0.0.1:5001
ENV CONSOLE_WEB_URL=http://127.0.0.1:3000
ENV SERVICE_API_URL=http://127.0.0.1:5001
ENV APP_WEB_URL=http://127.0.0.1:3000

EXPOSE 5001

# set timezone
ENV TZ=UTC

WORKDIR /app/api

RUN \
    apt-get update \
    # Install dependencies
    && apt-get install -y --no-install-recommends \
        # basic environment
        curl nodejs libgmp-dev libmpfr-dev libmpc-dev \
        # For Security
        expat libldap-2.5-0 perl libsqlite3-0 zlib1g \
        # install a chinese font to support the use of tools like matplotlib
        fonts-noto-cjk \
        # install a package to improve the accuracy of guessing mime type and file extension
        media-types \
        # install libmagic to support the use of python-magic guess MIMETYPE
        libmagic1 \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy Python environment and packages
ENV VIRTUAL_ENV=/app/api/.venv
COPY --from=packages ${VIRTUAL_ENV} ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Download nltk data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"

ENV TIKTOKEN_CACHE_DIR=/app/api/.tiktoken_cache
RUN python -c "import tiktoken; tiktoken.encoding_for_model('gpt2')"

FROM langgenius/dify-web:0.15.3 as web

# Final stage
FROM nginx:alpine

# Install dependencies
RUN apk add --no-cache supervisor python3 py3-pip nodejs npm

# Copy the Dify API files
COPY --from=production /app/api /app/api
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

[program:api]
directory=/app/api
command=/app/api/venv/bin/python app.py
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:web]
directory=/app/web
command=npm start
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:nginx]
command=nginx -g 'daemon off;'
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
EOF

# Set environment variables
ENV FLASK_APP=app.py
ENV EDITION=SELF_HOSTED
ENV DEPLOY_ENV=PRODUCTION
ENV CONSOLE_API_URL=http://127.0.0.1:5001
ENV CONSOLE_WEB_URL=http://127.0.0.1:3000
ENV SERVICE_API_URL=http://127.0.0.1:5001
ENV APP_WEB_URL=http://127.0.0.1:3000
ENV TZ=UTC

# Expose ports
EXPOSE 80

# Start supervisor which will start all services
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
