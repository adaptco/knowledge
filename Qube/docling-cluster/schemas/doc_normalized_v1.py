"""
Schema: doc.normalized.v1

Canonical representation of a parsed and normalized document.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SourceInfo(BaseModel):
    """Document source metadata."""
    uri: str
    content_type: str
    received_at: datetime


class ParserInfo(BaseModel):
    """Parser identification for reproducibility."""
    name: str = "ibm-docling"
    version: str
    config_hash: str


class TextPolicy(BaseModel):
    """Text normalization policy."""
    unicode: Literal["NFKC"] = "NFKC"
    whitespace: Literal["collapse"] = "collapse"
    line_endings: Literal["LF"] = "LF"


class NormalizationInfo(BaseModel):
    """Normalization metadata."""
    normalizer_version: str = "norm.v1"
    canonicalization: Literal["JCS-RFC8785"] = "JCS-RFC8785"
    text_policy: TextPolicy = Field(default_factory=TextPolicy)


class TextBlock(BaseModel):
    """A text block within a page."""
    type: Literal["text"] = "text"
    text: str


class TableBlock(BaseModel):
    """A table block within a page."""
    type: Literal["table"] = "table"
    cells: list[list[str]]


class PageContent(BaseModel):
    """Content of a single page."""
    page_index: int
    blocks: list[TextBlock | TableBlock]


class DocumentContent(BaseModel):
    """Full document content."""
    title: str | None = None
    pages: list[PageContent]


class IntegrityInfo(BaseModel):
    """Cryptographic integrity fields."""
    sha256_canonical: str
    prev_ledger_hash: str | None = None


class DocNormalizedV1(BaseModel):
    """
    doc.normalized.v1 schema.
    
    Canonical representation of a parsed document with full provenance
    and integrity information.
    """
    schema_: Literal["doc.normalized.v1"] = Field(
        default="doc.normalized.v1",
        alias="schema"
    )
    doc_id: str
    source: SourceInfo
    parser: ParserInfo
    normalization: NormalizationInfo = Field(default_factory=NormalizationInfo)
    content: DocumentContent
    integrity: IntegrityInfo

    class Config:
        populate_by_name = True
