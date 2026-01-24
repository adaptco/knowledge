"""
Capsule Model API

FastAPI service for agent capsule routing and LoRA weight management.
"""
import sys
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

sys.path.insert(0, "/app")
from schemas.capsule_v1 import (
    CapsuleModel,
    LoRAWeight,
    RoutingRequest,
    RoutingResponse
)
from router import get_capsule_manager
from lora_registry import get_lora_registry


app = FastAPI(
    title="Capsule Model API",
    description="Agent capsule routing and LoRA weight management",
    version="1.0.0"
)


class HealthResponse(BaseModel):
    status: str
    capsules_loaded: int


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    manager = get_capsule_manager()
    return HealthResponse(
        status="healthy",
        capsules_loaded=len(manager.capsules)
    )


@app.post("/route", response_model=RoutingResponse)
async def route_request(request: RoutingRequest, capsule_id: str = "default"):
    """
    Route a request to select appropriate LoRA weights.
    
    Args:
        request: Routing request with text and context
        capsule_id: Which capsule model to use
        
    Returns:
        RoutingResponse with selected LoRA ID
    """
    manager = get_capsule_manager()
    response = manager.route(capsule_id, request)
    
    if response is None:
        raise HTTPException(status_code=404, detail=f"Capsule '{capsule_id}' not found")
    
    return response


@app.post("/capsules")
async def register_capsule(capsule: CapsuleModel):
    """Register a new capsule model."""
    manager = get_capsule_manager()
    manager.register_capsule(capsule)
    return {"status": "registered", "capsule_id": capsule.capsule_id}


@app.get("/capsules")
async def list_capsules():
    """List all registered capsule models."""
    manager = get_capsule_manager()
    return {
        "capsules": [
            {"capsule_id": cid, "base_model_id": c.base_model_id}
            for cid, c in manager.capsules.items()
        ]
    }


@app.post("/lora/register")
async def register_lora(
    lora_weight: LoRAWeight,
    weights_file: UploadFile = File(...)
):
    """
    Register a new LoRA weight.
    
    Args:
        lora_weight: LoRA metadata
        weights_file: Binary weight file
    """
    registry = get_lora_registry()
    
    # Read weight data
    weights_data = await weights_file.read()
    
    # Register
    registry.register(lora_weight, weights_data)
    
    return {
        "status": "registered",
        "lora_id": lora_weight.lora_id,
        "size_bytes": len(weights_data)
    }


@app.get("/lora")
async def list_lora_weights():
    """List all registered LoRA weights."""
    registry = get_lora_registry()
    weights = registry.list_all()
    return {
        "lora_weights": [w.model_dump() for w in weights]
    }


@app.get("/lora/{lora_id}")
async def get_lora_weight(lora_id: str):
    """Get LoRA weight metadata."""
    registry = get_lora_registry()
    weight = registry.get(lora_id)
    
    if weight is None:
        raise HTTPException(status_code=404, detail=f"LoRA '{lora_id}' not found")
    
    return weight


@app.delete("/lora/{lora_id}")
async def delete_lora_weight(lora_id: str):
    """Delete a LoRA weight."""
    registry = get_lora_registry()
    success = registry.delete(lora_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"LoRA '{lora_id}' not found")
    
    return {"status": "deleted", "lora_id": lora_id}
