"""
Docling Worker - Document Parsing Service using RQ.
"""
import os
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from redis import Redis
from rq import Queue, Worker

# Add parent path for imports
sys.path.insert(0, "/app")
from lib import get_ledger, hash_canonical_without_integrity
from common.normalize import normalize_text

# Configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
DOCLING_VERSION = os.environ.get("DOCLING_VERSION", "2.0.0")

redis_conn = Redis.from_url(REDIS_URL)
embed_queue = Queue("embed_queue", connection=redis_conn)

def parse_document(job_payload: dict):
    """
    Worker task: Parse document and queue for embedding.
    """
    bundle_id = job_payload["bundle_id"]
    source_hash = job_payload["source_hash"]
    content_hex = job_payload["content_hex"]
    filename = job_payload["filename"]
    
    print(f"[docling-worker] Processing bundle {bundle_id}, doc {source_hash}")
    
    # Mock parse (replace with actual Docling logic)
    text_content = bytes.fromhex(content_hex).decode("utf-8", errors="replace")[:2000]
    normalized_text = normalize_text(text_content)
    
    doc_payload = {
        "schema": "doc.normalized.v1",
        "doc_id": source_hash,
        "source": {
            "uri": f"upload://{filename}",
            "content_type": "application/octet-stream",
            "received_at": job_payload["queued_at"]
        },
        "parser": {
            "name": "ibm-docling",
            "version": DOCLING_VERSION,
            "config_hash": "sha256:TODO"
        },
        "content": {
            "title": filename,
            "pages": [{
                "page_index": 0,
                "blocks": [{"type": "text", "text": normalized_text}]
            }]
        }
    }
    
    # Compute integrity
    sha256_canonical = hash_canonical_without_integrity(doc_payload)
    doc_payload["integrity"] = {
        "sha256_canonical": f"sha256:{sha256_canonical}",
        "prev_ledger_hash": get_ledger().get_prev_hash()
    }
    
    # Append to ledger
    get_ledger().append("doc.normalized.v1", doc_payload)
    
    # Queue for embedding
    # We chunk here or let the embed worker do it.
    # The user's embed_worker expects:
    # { "doc_id", "chunk_index", "chunk_text", "source_block_refs", "bundle_id" }
    
    print(f"[docling-worker] Chunking and queueing for embedding...")
    
    # Simple chunking for demonstration
    chunk_text = normalized_text[:1000] # Simple first chunk
    embed_payload = {
        "bundle_id": bundle_id,
        "doc_id": source_hash,
        "chunk_index": 0,
        "chunk_text": chunk_text,
        "source_block_refs": ["p0:b0"]
    }
    
    embed_queue.enqueue("worker.embed_chunk", embed_payload)
    
    return {"status": "parsed", "doc_id": source_hash}

if __name__ == "__main__":
    # Run as RQ worker
    worker = Worker(
        queues=[Queue("parse_queue", connection=redis_conn)],
        connection=redis_conn
    )
    worker.work()
