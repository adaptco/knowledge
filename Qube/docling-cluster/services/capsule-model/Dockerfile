FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY services/capsule-model/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY lib/ ./lib/
COPY schemas/ ./schemas/
COPY ledger/ ./ledger/

# Copy service code
COPY services/capsule-model/ ./

# Create data directory for LoRA registry
RUN mkdir -p /app/data/lora_registry

EXPOSE 8002

CMD ["uvicorn", "capsule_api:app", "--host", "0.0.0.0", "--port", "8002"]
