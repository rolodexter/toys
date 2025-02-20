FROM python:3.12-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY api/requirements.txt ./api/
RUN pip install --no-cache-dir -r api/requirements.txt

# Copy application code
COPY api/ ./api/
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Set environment variables
ENV PORT=3000

# Command to run the application
CMD ["/start.sh"]
