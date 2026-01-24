"""
Schema: capsule.v1

Agent Capsule Model schema for routing nodes and LoRA weight selection.
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field


class LoRAWeight(BaseModel):
    """LoRA (Low-Rank Adaptation) weight configuration."""
    lora_id: str
    rank: int = 8  # LoRA rank (typically 4-64)
    alpha: float = 16.0  # LoRA scaling factor
    weights_hash: str  # SHA256 of weight file
    domain: str  # e.g., "medical", "legal", "technical"
    description: Optional[str] = None


class RoutingNode(BaseModel):
    """Routing decision node for LoRA selection."""
    node_id: str
    condition: str  # Routing condition (e.g., "domain == 'medical'")
    lora_id: str  # Which LoRA to apply
    priority: int = 0  # Higher priority wins in conflicts


class CapsuleModel(BaseModel):
    """
    Agent Capsule Model.
    
    Encapsulates base model, routing logic, and LoRA weights
    for composable agent behavior.
    """
    schema_: Literal["capsule.v1"] = Field(
        default="capsule.v1",
        alias="schema"
    )
    capsule_id: str
    base_model_id: str  # Base embedding model
    routing_nodes: list[RoutingNode]
    lora_weights: dict[str, LoRAWeight]  # lora_id -> LoRAWeight
    metadata: dict = Field(default_factory=dict)

    class Config:
        populate_by_name = True


class RoutingRequest(BaseModel):
    """Request to route and select LoRA weights."""
    text: str
    context: dict = Field(default_factory=dict)  # e.g., {"domain": "medical"}


class RoutingResponse(BaseModel):
    """Response from routing decision."""
    lora_id: str
    confidence: float
    node_id: str
    applied_condition: str
