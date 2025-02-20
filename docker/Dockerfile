# Use the official Dify images
FROM langgenius/dify-api:0.15.3 as api
FROM langgenius/dify-web:0.15.3 as web

# Final stage
FROM nginx:alpine

# Install dependencies
RUN apk add --no-cache supervisor python3 py3-pip nodejs npm py3-virtualenv curl

# Copy the Dify API files first
COPY --from=api /app /app/api
WORKDIR /app/api

# Install poetry and dependencies
RUN python3 -m venv /app/api/venv && \
    . /app/api/venv/bin/activate && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    cd /app/api && \
    poetry install --no-root

ENV PATH="/app/api/venv/bin:$PATH"

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

# Expose ports
EXPOSE 80

# Start supervisor which will start all services
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
