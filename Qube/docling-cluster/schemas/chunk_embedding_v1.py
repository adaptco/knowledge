"""
Schema: chunk.embedding.v1

Canonical representation of a document chunk with its embedding vector.
"""
from typing import Literal

from pydantic import BaseModel, Field


class Chunker(BaseModel):
    """Chunker configuration for reproducibility."""
    version: str = "chunk.v1"
    method: str = "block+window"
    params: dict = Field(default_factory=lambda: {"max_tokens": 400, "overlap": 60})


class Embedding(BaseModel):
    """Embedding metadata and vector."""
    framework: Literal["pytorch"] = "pytorch"
    model_id: str
    weights_hash: str
    dim: int
    normalization: Literal["l2"] = "l2"
    vector: list[float]


class Provenance(BaseModel):
    """Links back to source blocks."""
    source_block_refs: list[str]  # e.g., ["p0:b12", "p0:b13"]


class IntegrityInfo(BaseModel):
    """Cryptographic integrity fields."""
    sha256_canonical: str
    prev_ledger_hash: str | None = None


class ChunkEmbeddingV1(BaseModel):
    """
    chunk.embedding.v1 schema.
    
    Represents a text chunk from a document with its embedding vector,
    full provenance, and integrity chain.
    """
    schema_: Literal["chunk.embedding.v1"] = Field(
        default="chunk.embedding.v1",
        alias="schema"
    )
    doc_id: str
    chunk_id: str
    chunk_text: str  # Added for worker compatibility
    chunker: Chunker = Field(default_factory=Chunker)
    embedding: Embedding
    provenance: Provenance
    integrity: IntegrityInfo | None = None  # Optional for late computation

    class Config:
        populate_by_name = True
