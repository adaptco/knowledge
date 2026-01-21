"""
Ledger Service - Append-only JSONL with hash-chain integrity.
"""
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Optional

app = FastAPI(title="Docling Ledger", version="1.0.0")

DATA_DIR = Path("/app/data")
LEDGER_FILE = DATA_DIR / "ledger.jsonl"

# In-memory state
last_hash: Optional[str] = None


class LedgerEntry(BaseModel):
    type: str
    bundle_id: str
    payload: Any


class LedgerRecord(BaseModel):
    seq: int
    timestamp: str
    type: str
    bundle_id: str
    payload_hash: str
    prev_hash: Optional[str]
    entry_hash: str


def compute_hash(data: dict) -> str:
    canonical = json.dumps(data, separators=(',', ':'), sort_keys=True)
    return f"sha256:{hashlib.sha256(canonical.encode()).hexdigest()}"


@app.on_event("startup")
async def startup():
    global last_hash
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Recover last hash from existing ledger
    if LEDGER_FILE.exists():
        with open(LEDGER_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    last_hash = record.get('entry_hash')
        print(f"Recovered ledger state. Last hash: {last_hash}")


@app.post("/append", response_model=LedgerRecord)
async def append_entry(entry: LedgerEntry):
    global last_hash
    
    # Read current sequence number
    seq = 0
    if LEDGER_FILE.exists():
        with open(LEDGER_FILE, 'r') as f:
            seq = sum(1 for _ in f)
    
    # Compute payload hash
    payload_hash = compute_hash(entry.payload if isinstance(entry.payload, dict) else {"value": entry.payload})
    
    # Build record
    record_data = {
        "seq": seq,
        "timestamp": datetime.utcnow().isoformat(),
        "type": entry.type,
        "bundle_id": entry.bundle_id,
        "payload_hash": payload_hash,
        "prev_hash": last_hash
    }
    
    # Compute entry hash (includes prev_hash for chain)
    entry_hash = compute_hash(record_data)
    record_data["entry_hash"] = entry_hash
    
    # Append to ledger
    with open(LEDGER_FILE, 'a') as f:
        f.write(json.dumps(record_data) + '\n')
    
    last_hash = entry_hash
    
    return LedgerRecord(**record_data)


@app.get("/verify")
async def verify_chain():
    """Verify the integrity of the hash chain."""
    if not LEDGER_FILE.exists():
        return {"status": "empty", "entries": 0}
    
    prev = None
    count = 0
    
    with open(LEDGER_FILE, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            
            # Check prev_hash linkage
            if record.get('prev_hash') != prev:
                return {"status": "broken", "at_seq": record['seq'], "reason": "prev_hash mismatch"}
            
            # Verify entry_hash
            check_data = {k: v for k, v in record.items() if k != 'entry_hash'}
            expected_hash = compute_hash(check_data)
            if record['entry_hash'] != expected_hash:
                return {"status": "broken", "at_seq": record['seq'], "reason": "entry_hash mismatch"}
            
            prev = record['entry_hash']
            count += 1
    
    return {"status": "verified", "entries": count, "head_hash": prev}


@app.get("/health")
async def health():
    return {"status": "healthy"}
