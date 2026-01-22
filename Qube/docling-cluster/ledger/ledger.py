"""
Ledger Service - FastAPI 
Manages the append-only JSONL ledger with hash-chain integrity.
"""
import json
import os
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add parent directory for imports
sys.path.insert(0, "/app")
from lib import jcs

app = FastAPI(title="Docling Ledger Service", version="0.2.0")

LEDGER_PATH = Path(os.environ.get("LEDGER_PATH", "/app/data/ledger.jsonl"))
LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)

class LedgerEntry(BaseModel):
    event: str
    bundle_id: str
    payload: dict[str, Any]

class LedgerRecord(BaseModel):
    timestamp: str
    event: str
    bundle_id: str
    payload: dict[str, Any]
    prev_hash: Optional[str]
    entry_hash: str

class Ledger:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()
        self._prev_hash = self._load_last_hash()

    def _load_last_hash(self) -> Optional[str]:
        if not self.path.exists():
            return None
        last_line = None
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line
        if last_line:
            try:
                entry = json.loads(last_line)
                return entry.get("entry_hash")
            except Exception:
                return None
        return None

    def append(self, event: str, bundle_id: str, payload: dict[str, Any]) -> dict:
        with self._lock:
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": event,
                "bundle_id": bundle_id,
                "payload": payload,
                "prev_hash": self._prev_hash
            }
            # Compute canonical hash
            canonical_json = jcs.canonicalize(record)
            entry_hash = f"sha256:{hashlib.sha256(canonical_json.encode()).hexdigest()}"
            record["entry_hash"] = entry_hash
            
            # Write to file
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(jcs.canonicalize(record) + "\n")
            
            self._prev_hash = entry_hash
            return record

    def get_prev_hash(self) -> Optional[str]:
        return self._prev_hash

import hashlib
ledger = Ledger(LEDGER_PATH)

@app.post("/append")
async def append_to_ledger(entry: LedgerEntry):
    try:
        record = ledger.append(entry.event, entry.bundle_id, entry.payload)
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prev_hash")
async def get_prev_hash():
    return {"prev_hash": ledger.get_prev_hash()}

@app.get("/health")
async def health():
    return {"status": "ok"}
