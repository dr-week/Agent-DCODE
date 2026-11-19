# Agent-DCODE Production Container Image
# Multi-platform lightweight runtime compatible with Hugging Face Spaces and Render free tier

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir flask flask-cors requests

COPY src/ /app/src/
COPY evals/ /app/evals/
COPY scripts/ /app/scripts/

RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/logs /app/projects && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["python3", "-m", "dcode.web.app"]
