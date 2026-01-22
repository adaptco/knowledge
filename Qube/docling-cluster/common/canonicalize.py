"""
JCS Canonicalization and SHA256 Hashing.

For deterministic JSON serialization and integrity verification.
"""
import hashlib
import json
from typing import Any


def jcs_canonical_bytes(obj: dict[str, Any]) -> bytes:
    """
    Serialize a dict to canonical JSON bytes (JCS-like).
    
    - Stable key ordering (sorted)
    - No whitespace
    - UTF-8 encoding
    
    For strict RFC 8785 compliance, use a dedicated JCS library.
    """
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    """Compute SHA-256 hash and return as hex string."""
    return hashlib.sha256(data).hexdigest()


def hash_canonical(payload: dict[str, Any]) -> str:
    """Hash a dict using JCS canonicalization."""
    return sha256_hex(jcs_canonical_bytes(payload))


def hash_canonical_without_integrity(payload: dict[str, Any]) -> str:
    """
    Hash a dict, excluding the 'integrity' field.
    
    This is the standard pattern for computing the hash of a payload
    where the hash will be stored in the integrity field itself.
    """
    tmp = dict(payload)
    tmp.pop("integrity", None)
    return sha256_hex(jcs_canonical_bytes(tmp))
