"""
LoRA Weight Registry

Manages storage and retrieval of LoRA (Low-Rank Adaptation) weights
for real-time model fine-tuning.
"""
import os
import json
from pathlib import Path
from typing import Optional
import sys

sys.path.insert(0, "/app")
from schemas.capsule_v1 import LoRAWeight


class LoRARegistry:
    """Registry for LoRA weights with file-based storage."""
    
    def __init__(self, registry_path: str = "/app/data/lora_registry"):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.registry_path / "index.json"
        self._index = self._load_index()
    
    def _load_index(self) -> dict:
        """Load the LoRA weight index."""
        if self.index_file.exists():
            with open(self.index_file, "r") as f:
                return json.load(f)
        return {}
    
    def _save_index(self):
        """Save the LoRA weight index."""
        with open(self.index_file, "w") as f:
            json.dump(self._index, f, indent=2)
    
    def register(self, lora_weight: LoRAWeight, weights_data: bytes):
        """
        Register a new LoRA weight.
        
        Args:
            lora_weight: LoRA weight metadata
            weights_data: Binary weight data
        """
        lora_id = lora_weight.lora_id
        
        # Save weight file
        weight_file = self.registry_path / f"{lora_id}.bin"
        with open(weight_file, "wb") as f:
            f.write(weights_data)
        
        # Update index
        self._index[lora_id] = lora_weight.model_dump()
        self._save_index()
    
    def get(self, lora_id: str) -> Optional[LoRAWeight]:
        """Get LoRA weight metadata by ID."""
        if lora_id in self._index:
            return LoRAWeight(**self._index[lora_id])
        return None
    
    def get_weights_path(self, lora_id: str) -> Optional[Path]:
        """Get path to LoRA weight file."""
        weight_file = self.registry_path / f"{lora_id}.bin"
        if weight_file.exists():
            return weight_file
        return None
    
    def list_all(self) -> list[LoRAWeight]:
        """List all registered LoRA weights."""
        return [LoRAWeight(**data) for data in self._index.values()]
    
    def delete(self, lora_id: str) -> bool:
        """Delete a LoRA weight."""
        if lora_id not in self._index:
            return False
        
        # Delete weight file
        weight_file = self.registry_path / f"{lora_id}.bin"
        if weight_file.exists():
            weight_file.unlink()
        
        # Remove from index
        del self._index[lora_id]
        self._save_index()
        return True


# Global registry instance
_registry: Optional[LoRARegistry] = None


def get_lora_registry(registry_path: Optional[str] = None) -> LoRARegistry:
    """Get or create the global LoRA registry instance."""
    global _registry
    if _registry is None:
        path = registry_path or os.environ.get("LORA_REGISTRY_PATH", "/app/data/lora_registry")
        _registry = LoRARegistry(path)
    return _registry
