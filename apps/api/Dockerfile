# Multi-stage Python API container for ETHIO-CYBERGUARD Backend
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition
COPY apps/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend codebase, services, and detection rules
COPY apps/api /app/apps/api
COPY services /app/services
COPY detection-rules /app/detection-rules
COPY collectors /app/collectors

EXPOSE 8000

ENV PYTHONPATH=/app

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
