"""
Embed Worker - Chunks text and generates embeddings.
Consumes from embed:pending, stores in Qdrant, logs to ledger.
"""
import os
import ast
import hashlib
from datetime import datetime
import redis
import httpx
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
LEDGER_URL = os.getenv("LEDGER_URL", "http://localhost:8001")

COLLECTION_NAME = "docling_chunks"
CHUNK_SIZE = 500
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 dimension

redis_client = redis.from_url(REDIS_URL)
qdrant_client = None


def init_qdrant():
    global qdrant_client
    qdrant_client = QdrantClient(url=QDRANT_URL)
    
    # Ensure collection exists
    collections = qdrant_client.get_collections().collections
    if COLLECTION_NAME not in [c.name for c in collections]:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
        )
        print(f"Created collection: {COLLECTION_NAME}")


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list:
    """Split text into chunks."""
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks


def embed_text(text: str) -> list:
    """
    Generate embedding for text.
    Placeholder: returns deterministic mock embedding based on text hash.
    In production, use sentence-transformers.
    """
    # Deterministic mock embedding for reproducibility
    h = hashlib.sha256(text.encode()).hexdigest()
    embedding = [int(h[i:i+2], 16) / 255.0 for i in range(0, min(len(h), EMBEDDING_DIM * 2), 2)]
    # Pad if necessary
    while len(embedding) < EMBEDDING_DIM:
        embedding.append(0.0)
    return embedding[:EMBEDDING_DIM]


def main():
    init_qdrant()
    print("Embed Worker started. Waiting for tasks...")
    
    while True:
        result = redis_client.blpop("embed:pending", timeout=5)
        
        if result is None:
            continue
            
        _, task_data = result
        task = ast.literal_eval(task_data.decode('utf-8'))
        
        print(f"Embedding: {task['bundle_id']}")
        
        chunks = chunk_text(task['text'])
        points = []
        
        for i, chunk_text_content in enumerate(chunks):
            chunk_id = hashlib.sha256(f"{task['doc_id']}:{i}".encode()).hexdigest()[:16]
            embedding = embed_text(chunk_text_content)
            
            chunk_record = {
                "id": chunk_id,
                "doc_id": task['doc_id'],
                "chunk_index": i,
                "text": chunk_text_content,
                "embedding": embedding,
                "metadata": {"model": "mock-embedder"},
                "embedded_at": datetime.utcnow().isoformat()
            }
            
            # Store in Qdrant
            points.append(PointStruct(
                id=i,
                vector=embedding,
                payload={"chunk_id": chunk_id, "doc_id": task['doc_id'], "text": chunk_text_content}
            ))
            
            # Log to ledger
            try:
                httpx.post(f"{LEDGER_URL}/append", json={
                    "type": "chunk.embedding.v1",
                    "bundle_id": task['bundle_id'],
                    "payload": chunk_record
                })
            except Exception as e:
                print(f"Ledger error: {e}")
        
        if points:
            qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
        
        print(f"Embedded {len(chunks)} chunks for {task['doc_id']}")


if __name__ == "__main__":
    main()
