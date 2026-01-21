FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (built from docling/ context)
COPY ingest_api/ ./ingest_api/
COPY common/ ./common/
COPY schemas/ ./schemas/
COPY ledger/ ./ledger/

WORKDIR /app/ingest_api

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
