"""
Pydantic request/response schemas for memory search endpoint.
"""

import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field


class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=8, ge=1, le=20)


class MemorySearchResultItem(BaseModel):
    chunk_id: str
    content_text: str
    score: float
    source_type: str
    source_id: Optional[str] = None
    module_key: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemorySearchResponse(BaseModel):
    results: list[MemorySearchResultItem]
    total: int
