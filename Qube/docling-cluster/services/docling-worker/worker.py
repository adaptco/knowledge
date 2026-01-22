"""
Docling Worker - Parses and normalizes documents.
Consumes from docling:pending, produces doc.normalized.v1, queues for embedding.
"""
import os
import ast
import time
import hashlib
from datetime import datetime
import redis
import httpx

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
LEDGER_URL = os.getenv("LEDGER_URL", "http://localhost:8001")

redis_client = redis.from_url(REDIS_URL)


def normalize_document(content: bytes, filename: str, source_hash: str) -> dict:
    """
    Parse and normalize a document into doc.normalized.v1 format.
    For now, treats all input as plain text.
    """
    text = content.decode('utf-8', errors='replace')
    
    # Simple structure detection (placeholder - real impl would use docling library)
    structure = []
    lines = text.split('\n')
    char_pos = 0
    for i, line in enumerate(lines):
        if line.startswith('#'):
            structure.append({
                "type": "heading",
                "start": char_pos,
                "end": char_pos + len(line),
                "level": len(line) - len(line.lstrip('#'))
            })
        elif line.strip():
            structure.append({
                "type": "paragraph",
                "start": char_pos,
                "end": char_pos + len(line)
            })
        char_pos += len(line) + 1
    
    doc_id = hashlib.sha256(source_hash.encode()).hexdigest()[:16]
    
    return {
        "id": doc_id,
        "source_hash": source_hash,
        "content": {
            "text": text,
            "structure": structure
        },
        "metadata": {
            "source_type": filename.split('.')[-1] if '.' in filename else "unknown"
        },
        "normalized_at": datetime.utcnow().isoformat()
    }


def main():
    print("Docling Worker started. Waiting for tasks...")
    
    while True:
        # Blocking pop from queue
        result = redis_client.blpop("docling:pending", timeout=5)
        
        if result is None:
            continue
            
        _, task_data = result
        task = ast.literal_eval(task_data.decode('utf-8'))
        
        print(f"Processing: {task['bundle_id']}")
        
        # Decode content
        content = bytes.fromhex(task['content_base64'])
        
        # Normalize
        normalized = normalize_document(
            content, 
            task['filename'], 
            task['source_hash']
        )
        
        # Log to ledger
        try:
            httpx.post(f"{LEDGER_URL}/append", json={
                "type": "doc.normalized.v1",
                "bundle_id": task['bundle_id'],
                "payload": normalized
            })
        except Exception as e:
            print(f"Ledger error: {e}")
        
        # Queue for embedding
        embed_task = {
            "bundle_id": task['bundle_id'],
            "doc_id": normalized['id'],
            "text": normalized['content']['text']
        }
        redis_client.rpush("embed:pending", str(embed_task))
        
        print(f"Completed: {task['bundle_id']} -> {normalized['id']}")


if __name__ == "__main__":
    main()
