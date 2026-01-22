FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (built from docling/ context)
COPY embed_worker/ ./embed_worker/
COPY lib/ ./lib/
COPY schemas/ ./schemas/
COPY ledger/ ./ledger/

WORKDIR /app/embed_worker

CMD ["python", "worker.py"]
