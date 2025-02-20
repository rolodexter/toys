FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-dev \
    libpq-dev \
    postgresql-server-dev-all \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/api/templates

# Copy application files
COPY api/app.py /app/api/
COPY api/models.py /app/api/
COPY api/templates/index.html /app/api/templates/
COPY api/templates/register.html /app/api/templates/

# Copy and setup start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FLASK_APP=/app/api/app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 8080

# Use CMD instead of ENTRYPOINT for more flexibility
CMD ["/bin/bash", "/app/start.sh"]
