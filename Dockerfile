# Multi-stage build for Dify deployment
FROM langgenius/dify-api:0.15.3 as api
FROM langgenius/dify-web:0.15.3 as web

# Final stage
FROM debian:bullseye-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy from API image
COPY --from=api /app /app/api
COPY --from=api /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy from Web image
COPY --from=web /app /app/web
COPY --from=web /usr/local/bin /usr/local/bin

# Copy Railway configuration
COPY docker/railway-compose.yaml /app/docker-compose.yaml
COPY railway.toml /app/railway.toml

WORKDIR /app

# Install Docker Compose
RUN curl -L "https://github.com/docker/compose/releases/download/v2.5.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Start script
COPY <<EOF /app/start.sh
#!/bin/bash
docker-compose -f docker-compose.yaml up -d
EOF

RUN chmod +x /app/start.sh

EXPOSE 3000 5001

CMD ["/app/start.sh"]
