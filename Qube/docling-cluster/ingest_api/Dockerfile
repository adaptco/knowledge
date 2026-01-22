FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ingest_api/ ./ingest_api/
COPY lib/ ./lib/
COPY schemas/ ./schemas/

WORKDIR /app/ingest_api

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
