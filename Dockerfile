FROM python:3.12-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpq-dev \
    postgresql-server-dev-all \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY api/requirements.txt ./api/
RUN pip install --no-cache-dir -r api/requirements.txt

# Copy API code, templates, and start script
COPY api/ ./api/
COPY start.sh /start.sh

# Set working directory to api folder
WORKDIR /app/api

RUN chmod +x /start.sh

CMD ["/start.sh"]
