# Use Python base image
FROM python:3.12-slim-bookworm as api

WORKDIR /app/api

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc g++ libc-dev libffi-dev libgmp-dev libmpfr-dev libmpc-dev \
    curl nodejs libgmp-dev libmpfr-dev libmpc-dev \
    expat libldap-2.5-0 perl libsqlite3-0 zlib1g \
    fonts-noto-cjk media-types libmagic1 \
    git make cmake pkg-config \
    libjpeg-dev libpng-dev libtiff-dev \
    libxml2-dev libxslt-dev \
    libssl-dev libffi-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy the Dify API files
COPY --from=langgenius/dify-api:0.15.3 /app /app/api

# Set up Python environment and install base dependencies
RUN python -m venv /app/api/venv && \
    . /app/api/venv/bin/activate && \
    pip install --upgrade pip setuptools wheel

# Install dependencies in groups
RUN . /app/api/venv/bin/activate && \
    pip install \
    flask==3.1.0 \
    flask-compress==1.17 \
    flask-cors==4.0.0 \
    flask-login==0.6.3 \
    flask-migrate==4.0.7 \
    flask-restful==0.3.10 \
    flask-sqlalchemy==3.1.1 \
    sqlalchemy==2.0.29 \
    gunicorn==23.0.0 \
    gevent==24.11.1

RUN . /app/api/venv/bin/activate && \
    pip install \
    nltk==3.9.1 \
    tiktoken==0.8.0 \
    numpy==1.26.4 \
    pandas[performance,excel]==2.2.2 \
    pandas-stubs==2.2.3.241009

RUN . /app/api/venv/bin/activate && \
    pip install \
    psycogreen==1.0.2 \
    psycopg2-binary==2.9.6 \
    redis[hiredis]==5.0.3

RUN . /app/api/venv/bin/activate && \
    pip install \
    pydantic==2.9.2 \
    pydantic-settings==2.6.0 \
    pydantic_extra_types==2.9.0 \
    starlette==0.41.0

RUN . /app/api/venv/bin/activate && \
    pip install \
    authlib==1.3.1 \
    pyjwt==2.8.0 \
    python-dotenv==1.0.1 \
    pyyaml==6.0.1

RUN . /app/api/venv/bin/activate && \
    pip install \
    beautifulsoup4==4.12.2 \
    bs4==0.0.1 \
    chardet==5.1.0 \
    markdown==3.5.1 \
    python-docx==1.1.0 \
    readabilipy==0.2.0 \
    unstructured[docx,epub,md,msg,ppt,pptx]==0.16.1

RUN . /app/api/venv/bin/activate && \
    pip install \
    azure-identity==1.16.1 \
    boto3==1.36.12 \
    google-api-core==2.18.0 \
    google-api-python-client==2.90.0 \
    google-auth==2.29.0 \
    google-auth-httplib2==0.2.0 \
    google-cloud-aiplatform==1.49.0 \
    googleapis-common-protos==1.63.0 \
    oci==2.135.1

RUN . /app/api/venv/bin/activate && \
    pip install \
    cachetools==5.3.0 \
    gmpy2==2.2.1 \
    httpx[socks]==0.27.0 \
    jieba==0.42.1 \
    langfuse==2.51.3 \
    langsmith==0.1.77 \
    openai==1.61.0 \
    openpyxl==3.1.5 \
    opik==1.3.4 \
    pypdfium2==4.30.0 \
    resend==0.7.0 \
    sentry-sdk[flask]==1.44.1 \
    tokenizers==0.15.0 \
    transformers==4.35.0 \
    validators==0.21.0 \
    yarl==1.18.3

# Download NLTK data and set up tiktoken
RUN . /app/api/venv/bin/activate && \
    python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')" && \
    python -c "import tiktoken; tiktoken.encoding_for_model('gpt2')"

# Set up tiktoken cache
ENV TIKTOKEN_CACHE_DIR=/app/api/.tiktoken_cache

FROM langgenius/dify-web:0.15.3 as web

# Final stage
FROM nginx:alpine

# Install dependencies
RUN apk add --no-cache supervisor python3 py3-pip nodejs npm

# Copy the Dify API files
COPY --from=api /app/api /app/api
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
