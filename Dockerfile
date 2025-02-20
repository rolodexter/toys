FROM python:3.12-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-dev \
    libpq-dev \
    postgresql-server-dev-all \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY api/requirements.txt ./api/
RUN pip install --no-cache-dir -r api/requirements.txt

# Create necessary directories and copy files
RUN mkdir -p /app/api/templates
COPY api/app.py /app/api/
COPY api/models.py /app/api/
COPY api/templates/* /app/api/templates/

# Set working directory to api folder
WORKDIR /app/api

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 8080

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--log-level", "debug", "--timeout", "0", "app:app"]
