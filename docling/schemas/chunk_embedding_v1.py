"""
Schema: chunk.embedding.v1

Canonical representation of a document chunk with its embedding vector.
"""
from typing import Literal

from pydantic import BaseModel, Field


class ChunkerInfo(BaseModel):
    """Chunker configuration for reproducibility."""
    version: str = "chunk.v1"
    method: str = "block+window"
    params: dict = Field(default_factory=lambda: {"max_tokens": 400, "overlap": 60})


class EmbeddingInfo(BaseModel):
    """Embedding metadata and vector."""
    framework: Literal["pytorch"] = "pytorch"
    model_id: str
    weights_hash: str
    dim: int
    normalization: Literal["l2"] = "l2"
    vector: list[float]


class ProvenanceInfo(BaseModel):
    """Links back to source blocks."""
    source_block_refs: list[str]  # e.g., ["p0:b12", "p0:b13"]


class IntegrityInfo(BaseModel):
    """Cryptographic integrity fields."""
    sha256_canonical: str
    prev_ledger_hash: str


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
    chunker: ChunkerInfo = Field(default_factory=ChunkerInfo)
    embedding: EmbeddingInfo
    provenance: ProvenanceInfo
    integrity: IntegrityInfo

    class Config:
        populate_by_name = True
