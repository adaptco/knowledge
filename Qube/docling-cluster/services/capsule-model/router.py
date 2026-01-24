"""
Capsule Router

Routing logic for selecting LoRA weights based on context and conditions.
"""
import sys
from typing import Optional

sys.path.insert(0, "/app")
from schemas.capsule_v1 import CapsuleModel, RoutingNode, RoutingRequest, RoutingResponse


class CapsuleRouter:
    """Routes embedding requests to appropriate LoRA weights."""
    
    def __init__(self, capsule: CapsuleModel):
        self.capsule = capsule
        # Sort routing nodes by priority (highest first)
        self.sorted_nodes = sorted(
            capsule.routing_nodes,
            key=lambda n: n.priority,
            reverse=True
        )
    
    def route(self, request: RoutingRequest) -> RoutingResponse:
        """
        Route a request to select the appropriate LoRA weight.
        
        Args:
            request: Routing request with text and context
            
        Returns:
            RoutingResponse with selected LoRA ID
        """
        # Evaluate routing nodes in priority order
        for node in self.sorted_nodes:
            if self._evaluate_condition(node.condition, request.context):
                return RoutingResponse(
                    lora_id=node.lora_id,
                    confidence=1.0,  # Deterministic routing
                    node_id=node.node_id,
                    applied_condition=node.condition
                )
        
        # Default: no LoRA (use base model)
        return RoutingResponse(
            lora_id="base",
            confidence=1.0,
            node_id="default",
            applied_condition="default"
        )
    
    def _evaluate_condition(self, condition: str, context: dict) -> bool:
        """
        Evaluate a routing condition.
        
        Supports simple equality checks:
        - "domain == 'medical'"
        - "language == 'en'"
        
        TODO: Extend with more complex logic (AND/OR, ranges, etc.)
        """
        try:
            # Simple equality parser
            if "==" in condition:
                key, value = condition.split("==")
                key = key.strip()
                value = value.strip().strip("'\"")
                
                return context.get(key) == value
            
            # TODO: Add more operators (!=, in, contains, etc.)
            return False
        except Exception:
            return False


class CapsuleManager:
    """Manages multiple capsule models."""
    
    def __init__(self):
        self.capsules: dict[str, CapsuleModel] = {}
        self.routers: dict[str, CapsuleRouter] = {}
    
    def register_capsule(self, capsule: CapsuleModel):
        """Register a new capsule model."""
        self.capsules[capsule.capsule_id] = capsule
        self.routers[capsule.capsule_id] = CapsuleRouter(capsule)
    
    def get_router(self, capsule_id: str) -> Optional[CapsuleRouter]:
        """Get router for a specific capsule."""
        return self.routers.get(capsule_id)
    
    def route(self, capsule_id: str, request: RoutingRequest) -> Optional[RoutingResponse]:
        """Route a request using a specific capsule."""
        router = self.get_router(capsule_id)
        if router:
            return router.route(request)
        return None


# Global capsule manager
_manager: Optional[CapsuleManager] = None


def get_capsule_manager() -> CapsuleManager:
    """Get or create the global capsule manager."""
    global _manager
    if _manager is None:
        _manager = CapsuleManager()
        _initialize_default_capsules(_manager)
    return _manager


def _initialize_default_capsules(manager: CapsuleManager):
    """Initialize default capsule models."""
    # Default capsule with domain-based routing
    default_capsule = CapsuleModel(
        capsule_id="default",
        base_model_id="all-MiniLM-L6-v2",
        routing_nodes=[
            RoutingNode(
                node_id="medical_route",
                condition="domain == 'medical'",
                lora_id="medical-v1",
                priority=10
            ),
            RoutingNode(
                node_id="legal_route",
                condition="domain == 'legal'",
                lora_id="legal-v1",
                priority=10
            ),
            RoutingNode(
                node_id="technical_route",
                condition="domain == 'technical'",
                lora_id="technical-v1",
                priority=10
            ),
        ],
        lora_weights={}  # Populated by registry
    )
    
    manager.register_capsule(default_capsule)
