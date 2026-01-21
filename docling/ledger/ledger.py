"""
Append-only JSONL Ledger with Hash-Chain.

Provides cryptographic integrity for all pipeline operations.
"""
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..common.canonicalize import hash_canonical, jcs_canonical_bytes


class Ledger:
    """
    Append-only JSONL ledger with hash-chain integrity.
    
    Each entry includes:
    - timestamp
    - event_type
    - payload
    - prev_hash (hash of previous entry)
    - entry_hash (hash of this entry)
    """
    
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._prev_hash: str | None = self._load_last_hash()
    
    def _load_last_hash(self) -> str | None:
        """Load the hash of the last entry, if any."""
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
            except json.JSONDecodeError:
                return None
        return None
    
    def append(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Append an entry to the ledger.
        
        Args:
            event_type: Type of event (e.g., "doc.normalized.v1", "chunk.embedding.v1")
            payload: Event payload (will be canonicalized)
            
        Returns:
            The complete ledger entry with hashes
        """
        with self._lock:
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": event_type,
                "payload": payload,
                "prev_hash": self._prev_hash,
            }
            
            # Compute entry hash (without entry_hash field)
            entry_hash = hash_canonical(entry)
            entry["entry_hash"] = entry_hash
            
            # Write to file
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(jcs_canonical_bytes(entry).decode("utf-8") + "\n")
            
            self._prev_hash = entry_hash
            return entry
    
    def get_prev_hash(self) -> str | None:
        """Get the hash of the last entry."""
        with self._lock:
            return self._prev_hash
    
    def verify(self) -> tuple[bool, list[str]]:
        """
        Verify the integrity of the entire ledger.
        
        Returns:
            (is_valid, list of error messages)
        """
        errors = []
        prev_hash = None
        line_num = 0
        
        if not self.path.exists():
            return True, []
        
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line_num += 1
                if not line.strip():
                    continue
                
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as e:
                    errors.append(f"Line {line_num}: Invalid JSON: {e}")
                    continue
                
                # Check prev_hash chain
                if entry.get("prev_hash") != prev_hash:
                    errors.append(
                        f"Line {line_num}: prev_hash mismatch. "
                        f"Expected {prev_hash}, got {entry.get('prev_hash')}"
                    )
                
                # Verify entry_hash
                stored_hash = entry.pop("entry_hash", None)
                computed_hash = hash_canonical(entry)
                entry["entry_hash"] = stored_hash  # Restore
                
                if stored_hash != computed_hash:
                    errors.append(
                        f"Line {line_num}: entry_hash mismatch. "
                        f"Expected {computed_hash}, got {stored_hash}"
                    )
                
                prev_hash = stored_hash
        
        return len(errors) == 0, errors


# Global ledger instance (lazy initialization)
_ledger: Ledger | None = None


def get_ledger(path: str | None = None) -> Ledger:
    """Get or create the global ledger instance."""
    global _ledger
    if _ledger is None:
        ledger_path = path or os.environ.get("LEDGER_PATH", "./data/ledger.jsonl")
        _ledger = Ledger(ledger_path)
    return _ledger
