FROM python:3.12-slim

WORKDIR /app

# Copy and install requirements
COPY api/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy application code
COPY api/app.py app.py
COPY api/models.py models.py
COPY api/templates templates/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 8080

# Run the application with Flask for development, Gunicorn for production
CMD if [ "$FLASK_ENV" = "development" ]; then \
        python -m flask run --host=0.0.0.0 --port=8080; \
    else \
        gunicorn --bind 0.0.0.0:8080 --workers 1 --log-level debug app:app; \
    fi
