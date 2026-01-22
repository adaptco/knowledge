FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY services/ledger/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY lib/ ./lib/
COPY schemas/ ./schemas/

# Copy service code
COPY services/ledger/ ./

EXPOSE 8001

CMD ["python", "server.py"]
