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
COPY services/docling-worker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY lib/ ./lib/
COPY schemas/ ./schemas/
COPY ledger/ ./ledger/

# Copy worker code
COPY services/docling-worker/tasks.py ./

CMD ["python", "tasks.py"]
