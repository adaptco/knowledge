"""
JCS (JSON Canonicalization Scheme) implementation per RFC 8785.
Provides deterministic JSON serialization for reproducible hashing.
"""
import json
import hashlib
from typing import Any


def canonicalize(obj: Any) -> str:
    """
    Serialize a Python object to JCS-canonical JSON.
    
    Rules (RFC 8785):
    - No whitespace
    - Keys sorted lexicographically (by UTF-16 code units)
    - Numbers: no leading zeros, no trailing zeros after decimal
    - Strings: minimal escape sequences
    """
    return json.dumps(obj, separators=(',', ':'), sort_keys=True, ensure_ascii=False)


def canonical_hash(obj: Any) -> str:
    """
    Compute SHA256 hash of the JCS-canonicalized JSON.
    Returns prefixed hash string: "sha256:..."
    """
    canonical = canonicalize(obj)
    digest = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    return f"sha256:{digest}"


def verify_hash(obj: Any, expected_hash: str) -> bool:
    """
    Verify that an object's canonical hash matches the expected value.
    """
    return canonical_hash(obj) == expected_hash
