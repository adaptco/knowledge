# Docling Pipeline

Document processing pipeline with deterministic hashing and vector embeddings.

## Quick Start

```bash
cd docling
docker-compose up --build
```

## Services

- **ingest-api** (port 8000) — Document submission endpoint
- **redis** (port 6379) — Task queues
- **qdrant** (port 6333) — Vector storage

## Usage

```bash
# Ingest a document
curl -X POST http://localhost:8000/ingest -F "file=@document.pdf"
```

## Tests

```bash
# Replay test (no services needed)
python tests/test_replay.py

# Integration test (requires docker-compose up)
python tests/test_integration.py
```
