"""
Pydantic request/response schemas for artifact endpoints.
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ArtifactVersionResponse(BaseModel):
    id: uuid.UUID
    artifact_id: uuid.UUID
    version_number: int
    content_json: dict[str, Any]
    content_markdown: Optional[str]
    change_summary: Optional[str]
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ArtifactResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    module_key: str
    artifact_type: str
    title: str
    content_json: dict[str, Any]
    content_markdown: Optional[str]
    source: str
    current_version_id: Optional[uuid.UUID]
    workflow_run_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ArtifactWithVersionsResponse(ArtifactResponse):
    versions: list[ArtifactVersionResponse] = []


class UpdateArtifactRequest(BaseModel):
    content_json: dict[str, Any] = Field(...)
    content_markdown: Optional[str] = None
    change_summary: Optional[str] = Field(default=None, max_length=500)


class ArtifactListResponse(BaseModel):
    items: list[ArtifactResponse]
    total: int
    skip: int
    limit: int
