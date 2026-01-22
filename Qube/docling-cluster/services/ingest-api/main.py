"""
Ingest API - FastAPI service for document submission.
Accepts documents and queues for processing using RQ.
"""
import os
import uuid
import hashlib
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from redis import Redis
from rq import Queue

app = FastAPI(title="Docling Ingest API", version="1.0.0")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = Redis.from_url(REDIS_URL)
parse_queue = Queue("parse_queue", connection=redis_conn)


class IngestResponse(BaseModel):
    bundle_id: str
    source_hash: str
    status: str
    queued_at: str


@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """
    Accept a document, compute its hash, and queue for processing using RQ.
    """
    content = await file.read()
    
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    # Compute source hash
    source_hash = f"sha256:{hashlib.sha256(content).hexdigest()}"
    bundle_id = str(uuid.uuid4())
    
    queued_at = datetime.utcnow().isoformat()

    # Queue task for docling-worker using RQ
    # The worker task is assumed to be 'tasks.parse_document' in the docling-worker service
    job_payload = {
        "bundle_id": bundle_id,
        "source_hash": source_hash,
        "filename": file.filename,
        "content_hex": content.hex(),
        "queued_at": queued_at
    }
    
    parse_queue.enqueue("tasks.parse_document", job_payload)
    
    return IngestResponse(
        bundle_id=bundle_id,
        source_hash=source_hash,
        status="queued",
        queued_at=queued_at
    )


@app.get("/health")
async def health():
    return {"status": "healthy"}
