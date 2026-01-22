"""
Embed Worker - Embedding Generation Service

Celery worker that chunks documents and generates embeddings using PyTorch.
"""
import hashlib
import os
import sys
from pathlib import Path
from typing import Any

from celery import Celery
import torch
from sentence_transformers import SentenceTransformer

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.canonicalize import hash_canonical, hash_canonical_without_integrity
from common.normalize import l2_normalize
from ledger import get_ledger


# Configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
QDRANT_HOST = os.environ.get("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
EMBEDDER_MODEL_ID = os.environ.get("EMBEDDER_MODEL_ID", "all-MiniLM-L6-v2")

# Chunker configuration
CHUNK_MAX_TOKENS = 400
CHUNK_OVERLAP = 60

# Celery app
celery_app = Celery("embed_worker", broker=REDIS_URL)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Global model (lazy loaded)
_model: SentenceTransformer | None = None
_weights_hash: str | None = None


def get_model() -> tuple[SentenceTransformer, str]:
    """Get or load the embedding model with weights hash."""
    global _model, _weights_hash
    
    if _model is None:
        print(f"[embed-worker] Loading model: {EMBEDDER_MODEL_ID}")
        _model = SentenceTransformer(EMBEDDER_MODEL_ID)
        
        # Compute weights hash for reproducibility
        state_dict = _model.state_dict()
        weights_bytes = b""
        for key in sorted(state_dict.keys()):
            weights_bytes += state_dict[key].cpu().numpy().tobytes()
        _weights_hash = hashlib.sha256(weights_bytes).hexdigest()
        
        print(f"[embed-worker] Model loaded, weights hash: {_weights_hash[:16]}...")
    
    return _model, _weights_hash


def chunk_document(doc_payload: dict) -> list[dict]:
    """
    Chunk a document into text segments.
    
    Uses a simple block-based chunking with overlap.
    """
    chunks = []
    chunk_idx = 0
    
    for page in doc_payload.get("content", {}).get("pages", []):
        page_idx = page["page_index"]
        
        for block_idx, block in enumerate(page.get("blocks", [])):
            if block["type"] == "text":
                text = block["text"]
                
                # Simple chunking by character count (replace with token-based in production)
                words = text.split()
                
                for i in range(0, len(words), CHUNK_MAX_TOKENS - CHUNK_OVERLAP):
                    chunk_words = words[i:i + CHUNK_MAX_TOKENS]
                    chunk_text = " ".join(chunk_words)
                    
                    if chunk_text.strip():
                        chunks.append({
                            "chunk_idx": chunk_idx,
                            "text": chunk_text,
                            "source_block_refs": [f"p{page_idx}:b{block_idx}"]
                        })
                        chunk_idx += 1
    
    return chunks


@celery_app.task(name="embed_worker.tasks.embed_document")
def embed_document(payload: dict) -> list[dict]:
    """
    Generate embeddings for a parsed document.
    
    Args:
        payload: {
            "bundle_id": str,
            "doc_payload": doc.normalized.v1 payload
        }
        
    Returns:
        List of chunk.embedding.v1 payloads
    """
    bundle_id = payload["bundle_id"]
    doc_payload = payload["doc_payload"]
    doc_id = doc_payload["doc_id"]
    
    print(f"[embed-worker] Processing bundle {bundle_id}, doc {doc_id}")
    
    # Get model and ledger
    model, weights_hash = get_model()
    ledger = get_ledger()
    
    # Chunk document
    chunks = chunk_document(doc_payload)
    print(f"[embed-worker] Created {len(chunks)} chunks")
    
    # Generate embeddings
    chunk_texts = [c["text"] for c in chunks]
    
    if not chunk_texts:
        print(f"[embed-worker] No text chunks to embed")
        return []
    
    # Encode with PyTorch
    with torch.no_grad():
        embeddings = model.encode(chunk_texts, convert_to_tensor=True)
        embeddings = l2_normalize(embeddings)
    
    # Build chunk.embedding.v1 payloads
    results = []
    
    for chunk, embedding in zip(chunks, embeddings):
        prev_ledger_hash = ledger.get_prev_hash()
        
        # Compute chunk_id
        chunk_content_hash = hashlib.sha256(chunk["text"].encode()).hexdigest()
        chunk_id = f"sha256:{chunk_content_hash}"
        
        chunk_payload = {
            "schema": "chunk.embedding.v1",
            "doc_id": doc_id,
            "chunk_id": chunk_id,
            "chunker": {
                "version": "chunk.v1",
                "method": "block+window",
                "params": {"max_tokens": CHUNK_MAX_TOKENS, "overlap": CHUNK_OVERLAP}
            },
            "embedding": {
                "framework": "pytorch",
                "model_id": EMBEDDER_MODEL_ID,
                "weights_hash": f"sha256:{weights_hash}",
                "dim": embedding.shape[-1],
                "normalization": "l2",
                "vector": embedding.tolist()
            },
            "provenance": {
                "source_block_refs": chunk["source_block_refs"]
            }
        }
        
        # Compute integrity
        canonical_hash = hash_canonical_without_integrity(chunk_payload)
        chunk_payload["integrity"] = {
            "sha256_canonical": f"sha256:{canonical_hash}",
            "prev_ledger_hash": prev_ledger_hash
        }
        
        # Append to ledger
        ledger.append("chunk.embedding.v1", chunk_payload)
        
        # Store in Qdrant
        _store_in_qdrant(chunk_id, embedding.tolist(), {
            "doc_id": doc_id,
            "chunk_id": chunk_id,
            "text": chunk["text"][:500]  # Store truncated text for retrieval
        })
        
        results.append(chunk_payload)
    
    print(f"[embed-worker] Completed {len(results)} embeddings for doc {doc_id}")
    return results


def _store_in_qdrant(chunk_id: str, vector: list[float], payload: dict):
    """
    Store embedding in Qdrant.
    
    Uses the Qdrant REST API directly for simplicity.
    In production, use the qdrant-client library.
    """
    import requests
    
    collection_name = "docling_chunks"
    
    # Ensure collection exists (simplified - should be done at startup)
    try:
        requests.put(
            f"http://{QDRANT_HOST}:{QDRANT_PORT}/collections/{collection_name}",
            json={
                "vectors": {
                    "size": len(vector),
                    "distance": "Cosine"
                }
            },
            timeout=5
        )
    except Exception:
        pass  # Collection may already exist
    
    # Upsert point
    point_id = int(hashlib.sha256(chunk_id.encode()).hexdigest()[:15], 16)
    
    try:
        requests.put(
            f"http://{QDRANT_HOST}:{QDRANT_PORT}/collections/{collection_name}/points",
            json={
                "points": [{
                    "id": point_id,
                    "vector": vector,
                    "payload": payload
                }]
            },
            timeout=10
        )
    except Exception as e:
        print(f"[embed-worker] Qdrant upsert failed: {e}")
