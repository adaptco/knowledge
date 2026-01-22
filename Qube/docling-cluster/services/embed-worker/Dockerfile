FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY services/embed-worker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY lib/ ./lib/
COPY schemas/ ./schemas/
COPY ledger/ ./ledger/

# Copy worker code
COPY services/embed-worker/worker.py ./

CMD ["python", "worker.py"]
