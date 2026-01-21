"""
Ingest API - FastAPI Service

Accepts document uploads and enqueues them for parsing.
"""
import hashlib
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from celery import Celery
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# Configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
DATA_DIR = Path(os.environ.get("DATA_DIR", "/app/data"))
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Celery client
celery_app = Celery("docling", broker=REDIS_URL)

# FastAPI app
app = FastAPI(
    title="Docling Ingest API",
    description="Document ingestion endpoint for the Docling pipeline",
    version="0.1.0",
)


class IngestResponse(BaseModel):
    """Response from document ingestion."""
    bundle_id: str
    doc_id: str
    status: str
    message: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """
    Ingest a document for processing.
    
    - Computes content hash (doc_id)
    - Saves file to upload directory
    - Enqueues parsing task
    - Returns bundle_id for tracking
    """
    # Read file content
    content = await file.read()
    
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    # Compute doc_id from content hash
    content_hash = hashlib.sha256(content).hexdigest()
    doc_id = f"sha256:{content_hash}"
    
    # Generate bundle_id
    bundle_id = str(uuid.uuid4())
    
    # Determine content type
    content_type = file.content_type or "application/octet-stream"
    
    # Save file
    file_ext = Path(file.filename or "document").suffix or ".bin"
    upload_path = UPLOAD_DIR / f"{content_hash}{file_ext}"
    
    with open(upload_path, "wb") as f:
        f.write(content)
    
    # Prepare task payload
    task_payload = {
        "bundle_id": bundle_id,
        "doc_id": doc_id,
        "file_path": str(upload_path),
        "content_type": content_type,
        "original_filename": file.filename,
        "received_at": datetime.now(timezone.utc).isoformat(),
    }
    
    # Enqueue parsing task
    celery_app.send_task("docling_worker.tasks.parse_document", args=[task_payload])
    
    return IngestResponse(
        bundle_id=bundle_id,
        doc_id=doc_id,
        status="queued",
        message=f"Document queued for parsing. Track with bundle_id: {bundle_id}"
    )


@app.get("/status/{bundle_id}")
async def get_status(bundle_id: str):
    """
    Get the status of a processing bundle.
    
    TODO: Implement status tracking via Redis or database.
    """
    return JSONResponse(
        content={
            "bundle_id": bundle_id,
            "status": "pending",
            "message": "Status tracking not yet implemented"
        }
    )
