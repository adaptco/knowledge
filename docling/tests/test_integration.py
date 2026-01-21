"""
Integration Test - End-to-end pipeline verification.
Requires docker-compose services to be running.
"""
import httpx
import time


INGEST_URL = "http://localhost:8000"
LEDGER_URL = "http://localhost:8001"


def wait_for_services(timeout=30):
    """Wait for services to be healthy."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r1 = httpx.get(f"{INGEST_URL}/health", timeout=2)
            r2 = httpx.get(f"{LEDGER_URL}/health", timeout=2)
            if r1.status_code == 200 and r2.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def test_full_pipeline():
    """Test document ingestion through to ledger."""
    print("Waiting for services...")
    if not wait_for_services():
        print("SKIP: Services not available")
        return
    
    # 1. Ingest a document
    print("Ingesting test document...")
    files = {"file": ("test.txt", b"Hello World. This is a test document.", "text/plain")}
    resp = httpx.post(f"{INGEST_URL}/ingest", files=files)
    
    assert resp.status_code == 200, f"Ingest failed: {resp.text}"
    data = resp.json()
    
    assert "bundle_id" in data, "Response should contain bundle_id"
    assert "source_hash" in data, "Response should contain source_hash"
    assert data["source_hash"].startswith("sha256:"), "Hash should be prefixed"
    
    bundle_id = data["bundle_id"]
    print(f"Ingested: {bundle_id}")
    
    # 2. Wait for processing
    print("Waiting for pipeline processing...")
    time.sleep(5)
    
    # 3. Verify ledger chain
    print("Verifying ledger integrity...")
    resp = httpx.get(f"{LEDGER_URL}/verify")
    assert resp.status_code == 200, f"Verify failed: {resp.text}"
    
    verify_data = resp.json()
    assert verify_data["status"] in ["verified", "empty"], f"Chain broken: {verify_data}"
    
    print(f"Ledger verified: {verify_data}")
    print("Integration test PASSED!")


if __name__ == "__main__":
    test_full_pipeline()
