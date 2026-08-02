"""
Pydantic request/response schemas for project and module endpoints.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Module schemas ─────────────────────────────────────────────────────────

class ProjectModuleResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    module_key: str
    display_name: str
    status: str
    sort_order: int
    last_run_id: Optional[uuid.UUID]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Project schemas ────────────────────────────────────────────────────────

class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    idea_brief: str = Field(min_length=10)
    tagline: Optional[str] = Field(default=None, max_length=500)
    industry: Optional[str] = Field(default=None, max_length=100)


class UpdateProjectRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    tagline: Optional[str] = Field(default=None, max_length=500)
    idea_brief: Optional[str] = Field(default=None, min_length=10)
    industry: Optional[str] = Field(default=None, max_length=100)
    stage: Optional[str] = Field(default=None, max_length=50)


class ProjectResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    tagline: Optional[str]
    idea_brief: str
    industry: Optional[str]
    stage: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectWithModulesResponse(ProjectResponse):
    modules: list[ProjectModuleResponse] = []


class ProjectListResponse(BaseModel):
    items: list[ProjectWithModulesResponse]
    total: int
    skip: int
    limit: int
