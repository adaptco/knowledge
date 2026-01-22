FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY services/ingest-api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY lib/ ./lib/
COPY schemas/ ./schemas/
COPY ledger/ ./ledger/

# Copy application code
COPY services/ingest-api/main.py ./

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
