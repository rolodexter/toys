FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-dev \
    libpq-dev \
    postgresql-server-dev-all \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create api directory
RUN mkdir -p /app/api/templates

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY app.py api/
COPY api/models.py api/
COPY api/templates/index.html api/templates/
COPY api/templates/register.html api/templates/

# Copy and setup start script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FLASK_APP=/app/api/app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 8080

# Use start.sh as entrypoint
ENTRYPOINT ["/start.sh"]
