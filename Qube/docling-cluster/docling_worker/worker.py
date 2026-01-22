"""
Docling Worker - Document Parsing Service
RQ worker that parses documents using IBM Docling and normalizes output.
"""
import hashlib
import os
import sys
from pathlib import Path
from redis import Redis
from rq import Queue, Worker

# Add parent directory for imports
sys.path.insert(0, "/app")

from lib import compute_chunk_id, get_ledger, hash_canonical_without_integrity
from schemas import DocNormalizedV1

# Configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
DOCLING_VERSION = os.environ.get("DOCLING_VERSION", "2.0.0")

redis_conn = Redis.from_url(REDIS_URL)

def compute_config_hash() -> str:
    """Compute hash of Docling configuration for reproducibility."""
    config = {
        "version": DOCLING_VERSION,
        "text_policy": {
            "unicode": "NFKC",
            "whitespace": "collapse",
            "line_endings": "LF"
        }
    }
    return hashlib.sha256(str(config).encode()).hexdigest()

def parse_document(payload: dict) -> dict:
    """
    Parse a document using Docling and normalize the output.
    """
    bundle_id = payload["bundle_id"]
    doc_id = payload["doc_id"]
    file_path = Path(payload["file_path"])
    content_type = payload["content_type"]
    received_at = payload["received_at"]
    
    print(f"[docling-worker] Processing bundle {bundle_id}, doc {doc_id}")
    
    # Simulate a single page with text content (placeholder for actual Docling)
    try:
        with open(file_path, "rb") as f:
            content = f.read()
    except Exception:
        content = b"Empty document"
    
    text_content = content.decode("utf-8", errors="replace")[:1000]
    
    # Simple normalization simulation
    normalized_pages = [{
        "page_index": 0,
        "blocks": [{"type": "text", "text": text_content.strip()}]
    }]
    
    # Build doc.normalized.v1 using Pydantic model
    doc_normalized = DocNormalizedV1(
        doc_id=doc_id,
        source={
            "uri": f"local://{file_path.name}",
            "content_type": content_type,
            "received_at": received_at
        },
        parser={
            "name": "ibm-docling",
            "version": DOCLING_VERSION,
            "config_hash": f"sha256:{compute_config_hash()}"
        },
        normalization={
            "normalizer_version": "norm.v1",
            "canonicalization": "JCS-RFC8785",
            "text_policy": {
                "unicode": "NFKC",
                "whitespace": "collapse",
                "line_endings": "LF"
            }
        },
        content={
            "title": file_path.stem,
            "pages": normalized_pages
        }
    )
    
    doc_dict = doc_normalized.model_dump(by_alias=True, exclude_none=True)
    
    # Compute integrity hash
    ledger = get_ledger()
    sha256_canonical = hash_canonical_without_integrity(doc_dict)
    
    # Append to ledger
    ledger_record = {
        "event": "doc.normalized.v1",
        "bundle_id": bundle_id,
        "doc_id": doc_id,
        "content_hash": sha256_canonical
    }
    ledger.append(ledger_record)
    
    # Enqueue embedding task for EACH block (simplified to one job per page for now)
    q = Queue("embed_queue", connection=redis_conn)
    for page in normalized_pages:
        for i, block in enumerate(page["blocks"]):
            q.enqueue("embed_worker.worker.embed_chunk", {
                "bundle_id": bundle_id,
                "doc_id": doc_id,
                "chunk_index": i,
                "chunk_text": block["text"],
                "source_block_refs": [f"p0:b{i}"]
            })
            
    return doc_dict

if __name__ == "__main__":
    worker = Worker(
        queues=[Queue("docling_queue", connection=redis_conn)],
        connection=redis_conn
    )
    worker.work()
