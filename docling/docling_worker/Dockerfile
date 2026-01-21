FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Docling
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpoppler-cpp-dev \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (built from docling/ context)
COPY docling_worker/ ./docling_worker/
COPY common/ ./common/
COPY schemas/ ./schemas/
COPY ledger/ ./ledger/

WORKDIR /app/docling_worker

CMD ["celery", "-A", "tasks", "worker", "--loglevel=info", "-Q", "parse_queue"]
