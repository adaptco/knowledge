"""
Ingest API - FastAPI service for document submission.
Accepts documents, computes source hash, and queues for processing.
"""
import os
import uuid
import hashlib
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import redis.asyncio as redis

app = FastAPI(title="Docling Ingest API", version="1.0.0")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = None


class IngestResponse(BaseModel):
    bundle_id: str
    source_hash: str
    status: str
    queued_at: str


@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = redis.from_url(REDIS_URL)


@app.on_event("shutdown")
async def shutdown():
    if redis_client:
        await redis_client.close()


@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """
    Accept a document, compute its hash, and queue for processing.
    """
    content = await file.read()
    
    # Compute source hash
    source_hash = f"sha256:{hashlib.sha256(content).hexdigest()}"
    bundle_id = str(uuid.uuid4())
    
    # Queue task for docling-worker
    task = {
        "bundle_id": bundle_id,
        "source_hash": source_hash,
        "filename": file.filename,
        "content_base64": content.hex(),  # Store as hex for JSON compatibility
        "queued_at": datetime.utcnow().isoformat()
    }
    
    await redis_client.rpush("docling:pending", str(task))
    
    return IngestResponse(
        bundle_id=bundle_id,
        source_hash=source_hash,
        status="queued",
        queued_at=task["queued_at"]
    )


@app.get("/health")
async def health():
    return {"status": "healthy"}
