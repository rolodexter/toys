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

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY app.py .
COPY api/models.py models.py
COPY api/templates templates/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 8080

# Run gunicorn directly
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--log-level", "debug", "app:app"]
