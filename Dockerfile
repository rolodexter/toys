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

# Create api directory structure
RUN mkdir -p /app/api/templates

# Copy files with explicit paths
COPY api/app.py /app/api/
COPY api/models.py /app/api/
COPY api/templates/index.html /app/api/templates/
COPY api/templates/register.html /app/api/templates/
COPY start.sh /start.sh

# Set working directory to api folder
WORKDIR /app/api

# Verify files exist
RUN ls -la /app/api && \
    ls -la /app/api/templates && \
    chmod +x /start.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1

CMD ["/start.sh"]
