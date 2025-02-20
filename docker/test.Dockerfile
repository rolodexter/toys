FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY docker/requirements.txt .
RUN pip install -r requirements.txt

CMD ["python", "-c", "import flask, langchain, unstructured; print('All dependencies installed successfully!')"]
