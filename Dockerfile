FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py wsgi.py ./

ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 8080

CMD ["gunicorn", \
    "--bind", "0.0.0.0:8080", \
    "--workers", "1", \
    "--log-level", "debug", \
    "--capture-output", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "--timeout", "300", \
    "wsgi:app"]
