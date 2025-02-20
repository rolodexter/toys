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
COPY app.py /app/api/app.py
COPY api/models.py /app/api/models.py
COPY api/templates/index.html /app/api/templates/index.html
COPY api/templates/register.html /app/api/templates/register.html

# Copy and setup start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FLASK_APP=/app/api/app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Start the application
CMD ["bash", "/app/start.sh"]
