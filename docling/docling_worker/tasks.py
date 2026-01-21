"""
Docling Worker - Document Parsing Service

Celery worker that parses documents using IBM Docling and normalizes output.
"""
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from celery import Celery

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.canonicalize import hash_canonical_without_integrity
from common.normalize import normalize_text
from ledger import get_ledger


# Configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
DOCLING_VERSION = os.environ.get("DOCLING_VERSION", "2.0.0")  # Pin version

# Celery app
celery_app = Celery("docling_worker", broker=REDIS_URL)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


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


@celery_app.task(name="docling_worker.tasks.parse_document")
def parse_document(payload: dict) -> dict:
    """
    Parse a document using Docling and normalize the output.
    
    Args:
        payload: {
            "bundle_id": str,
            "doc_id": str,
            "file_path": str,
            "content_type": str,
            "original_filename": str,
            "received_at": str (ISO format)
        }
        
    Returns:
        doc.normalized.v1 payload
    """
    bundle_id = payload["bundle_id"]
    doc_id = payload["doc_id"]
    file_path = Path(payload["file_path"])
    content_type = payload["content_type"]
    received_at = payload["received_at"]
    
    print(f"[docling-worker] Processing bundle {bundle_id}, doc {doc_id}")
    
    # Get ledger for hash chain
    ledger = get_ledger()
    prev_ledger_hash = ledger.get_prev_hash()
    
    # Parse document with Docling
    # NOTE: This is a placeholder. In production, use:
    # from docling.document_converter import DocumentConverter
    # converter = DocumentConverter()
    # result = converter.convert(str(file_path))
    
    # Simulated Docling output (replace with actual Docling call)
    raw_pages = _simulate_docling_parse(file_path)
    
    # Normalize text content
    normalized_pages = []
    for page_idx, page in enumerate(raw_pages):
        normalized_blocks = []
        for block_idx, block in enumerate(page.get("blocks", [])):
            if block["type"] == "text":
                normalized_text = normalize_text(block["text"])
                normalized_blocks.append({
                    "type": "text",
                    "text": normalized_text
                })
            elif block["type"] == "table":
                # Tables: normalize cell text
                normalized_cells = [
                    [normalize_text(cell) for cell in row]
                    for row in block.get("cells", [])
                ]
                normalized_blocks.append({
                    "type": "table",
                    "cells": normalized_cells
                })
        
        normalized_pages.append({
            "page_index": page_idx,
            "blocks": normalized_blocks
        })
    
    # Build doc.normalized.v1 payload
    doc_payload = {
        "schema": "doc.normalized.v1",
        "doc_id": doc_id,
        "source": {
            "uri": f"local://{file_path}",
            "content_type": content_type,
            "received_at": received_at
        },
        "parser": {
            "name": "ibm-docling",
            "version": DOCLING_VERSION,
            "config_hash": f"sha256:{compute_config_hash()}"
        },
        "normalization": {
            "normalizer_version": "norm.v1",
            "canonicalization": "JCS-RFC8785",
            "text_policy": {
                "unicode": "NFKC",
                "whitespace": "collapse",
                "line_endings": "LF"
            }
        },
        "content": {
            "title": file_path.stem,
            "pages": normalized_pages
        }
    }
    
    # Compute integrity hash
    canonical_hash = hash_canonical_without_integrity(doc_payload)
    doc_payload["integrity"] = {
        "sha256_canonical": f"sha256:{canonical_hash}",
        "prev_ledger_hash": prev_ledger_hash
    }
    
    # Append to ledger
    ledger.append("doc.normalized.v1", doc_payload)
    
    print(f"[docling-worker] Completed doc {doc_id}, hash: {canonical_hash[:16]}...")
    
    # Enqueue embedding task
    celery_app.send_task(
        "embed_worker.tasks.embed_document",
        args=[{
            "bundle_id": bundle_id,
            "doc_payload": doc_payload
        }]
    )
    
    return doc_payload


def _simulate_docling_parse(file_path: Path) -> list[dict]:
    """
    Simulate Docling parsing output.
    
    In production, replace this with actual Docling:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(str(file_path))
    """
    # Read file content for simulation
    try:
        with open(file_path, "rb") as f:
            content = f.read()
    except Exception:
        content = b"Empty document"
    
    # Simulate a single page with text content
    text_content = content.decode("utf-8", errors="replace")[:1000]
    
    return [
        {
            "blocks": [
                {"type": "text", "text": text_content}
            ]
        }
    ]
