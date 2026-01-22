import hashlib
from typing import Any
from . import jcs

def compute_chunk_id(doc_id: str, index: int, text: str) -> str:
    """Compute deterministic chunk ID."""
    content = f"{doc_id}:{index}:{text}"
    return f"sha256:{hashlib.sha256(content.encode()).hexdigest()}"

def hash_canonical_without_integrity(obj: Any) -> str:
    """Compute canonical hash of object excluding integrity field."""
    if "integrity" in obj:
        obj_copy = obj.copy()
        del obj_copy["integrity"]
        return jcs.canonical_hash(obj_copy)
    return jcs.canonical_hash(obj)

def get_ledger():
    """Client for the ledger service."""
    import os
    import requests
    class LedgerClient:
        def __init__(self):
            self.url = os.environ.get("LEDGER_URL", "http://ledger:8001")
        def append(self, record: dict):
            try:
                # We expect record to have 'event', 'bundle_id', 'payload'
                # But the workers pass simple dicts sometimes.
                # Alignment check:
                # docling-worker passes: {"event": "doc.normalized.v1", "bundle_id": bundle_id, "doc_id": doc_id, "content_hash": sha256_canonical}
                # embed-worker passes: {"event": "chunk.embedding.v1", "bundle_id": bundle_id, "doc_id": doc_id, "chunk_id": chunk_id, "chunk_index": chunk_index, ...}
                
                # The Ledger API expects LedgerEntry(event, bundle_id, payload)
                # We wrap the extra fields into payload if needed.
                event = record.get("event", "generic")
                bundle_id = record.get("bundle_id", "unknown")
                payload = {k: v for k, v in record.items() if k not in ["event", "bundle_id"]}
                
                requests.post(f"{self.url}/append", json={
                    "event": event,
                    "bundle_id": bundle_id,
                    "payload": payload
                }, timeout=5)
            except Exception as e:
                print(f"[LEDGER-CLIENT-ERROR] {e}")
    return LedgerClient()
