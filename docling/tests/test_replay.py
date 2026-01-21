"""
Replay Test - Verify deterministic hashing.
Same input should always produce identical hashes.
"""
import json
import hashlib


def canonicalize(obj):
    """JCS-canonical JSON serialization."""
    return json.dumps(obj, separators=(',', ':'), sort_keys=True, ensure_ascii=False)


def canonical_hash(obj):
    """SHA256 of canonical JSON."""
    canonical = canonicalize(obj)
    return f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


def verify_hash(obj, expected):
    """Verify hash matches."""
    return canonical_hash(obj) == expected



def test_jcs_determinism():
    """Same object should always produce same canonical form."""
    obj1 = {"b": 2, "a": 1, "c": {"z": 26, "y": 25}}
    obj2 = {"a": 1, "c": {"y": 25, "z": 26}, "b": 2}  # Same but different order
    
    assert canonicalize(obj1) == canonicalize(obj2), "Canonicalization should be order-independent"
    assert canonical_hash(obj1) == canonical_hash(obj2), "Hashes should match"


def test_hash_reproducibility():
    """Hash of a document should be reproducible."""
    doc = {
        "id": "test123",
        "content": {"text": "Hello World"},
        "metadata": {"author": "test"}
    }
    
    hash1 = canonical_hash(doc)
    hash2 = canonical_hash(doc)
    
    assert hash1 == hash2, "Same document should have same hash"
    assert hash1.startswith("sha256:"), "Hash should have prefix"


def test_hash_verification():
    """verify_hash should correctly validate."""
    doc = {"test": "value"}
    h = canonical_hash(doc)
    
    assert verify_hash(doc, h) is True, "Valid hash should verify"
    assert verify_hash(doc, "sha256:invalid") is False, "Invalid hash should fail"


def test_different_content_different_hash():
    """Different content should produce different hashes."""
    doc1 = {"content": "version1"}
    doc2 = {"content": "version2"}
    
    assert canonical_hash(doc1) != canonical_hash(doc2), "Different content = different hash"


if __name__ == "__main__":
    test_jcs_determinism()
    test_hash_reproducibility()
    test_hash_verification()
    test_different_content_different_hash()
    print("All replay tests passed!")
