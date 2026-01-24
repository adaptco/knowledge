#!/usr/bin/env python3
"""
Test script for Agent Capsule Model System

Tests routing node selection and LoRA weight management.
"""
import requests
import json

CAPSULE_URL = "http://localhost:8002"


def test_health():
    """Test capsule-model health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{CAPSULE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Health check passed\n")


def test_routing():
    """Test routing node selection."""
    print("Testing routing node selection...")
    
    test_cases = [
        {
            "text": "Patient diagnosed with hypertension",
            "context": {"domain": "medical"},
            "expected_lora": "medical-v1"
        },
        {
            "text": "Contract terms and conditions",
            "context": {"domain": "legal"},
            "expected_lora": "legal-v1"
        },
        {
            "text": "API documentation for REST endpoints",
            "context": {"domain": "technical"},
            "expected_lora": "technical-v1"
        },
        {
            "text": "Generic text without domain",
            "context": {},
            "expected_lora": "base"
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest case {i+1}: {test_case['context']}")
        response = requests.post(
            f"{CAPSULE_URL}/route",
            json={
                "text": test_case["text"],
                "context": test_case["context"]
            },
            params={"capsule_id": "default"}
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Selected LoRA: {result['lora_id']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Node ID: {result['node_id']}")
        
        assert result["lora_id"] == test_case["expected_lora"], \
            f"Expected {test_case['expected_lora']}, got {result['lora_id']}"
        print("✓ Routing test passed")
    
    print("\n✓ All routing tests passed\n")


def test_lora_registry():
    """Test LoRA weight registration and retrieval."""
    print("Testing LoRA registry...")
    
    # Register a test LoRA weight
    lora_metadata = {
        "lora_id": "test-lora-v1",
        "rank": 8,
        "alpha": 16.0,
        "weights_hash": "sha256:test_hash_123",
        "domain": "test",
        "description": "Test LoRA weight"
    }
    
    # Create dummy weights file
    dummy_weights = b"dummy_weights_data"
    
    print("Registering test LoRA...")
    response = requests.post(
        f"{CAPSULE_URL}/lora/register",
        data={"lora_weight": json.dumps(lora_metadata)},
        files={"weights_file": ("test.bin", dummy_weights)}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ LoRA registration passed")
    
    # List all LoRA weights
    print("\nListing all LoRA weights...")
    response = requests.get(f"{CAPSULE_URL}/lora")
    print(f"Status: {response.status_code}")
    lora_list = response.json()
    print(f"Found {len(lora_list['lora_weights'])} LoRA weights")
    assert response.status_code == 200
    print("✓ LoRA listing passed")
    
    # Get specific LoRA
    print("\nGetting specific LoRA...")
    response = requests.get(f"{CAPSULE_URL}/lora/test-lora-v1")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ LoRA retrieval passed")
    
    # Delete test LoRA
    print("\nDeleting test LoRA...")
    response = requests.delete(f"{CAPSULE_URL}/lora/test-lora-v1")
    print(f"Status: {response.status_code}")
    assert response.status_code == 200
    print("✓ LoRA deletion passed")
    
    print("\n✓ All LoRA registry tests passed\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Agent Capsule Model System - Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_routing()
        test_lora_registry()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
