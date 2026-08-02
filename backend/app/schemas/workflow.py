"""
Pydantic request/response schemas for workflow endpoints.
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class WorkflowStepResponse(BaseModel):
    id: uuid.UUID
    workflow_run_id: uuid.UUID
    step_key: str
    status: str
    sequence: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    metadata_json: Optional[dict[str, Any]]
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkflowRunResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    module_key: str
    status: str
    triggered_by: Optional[uuid.UUID]
    input_snapshot: dict[str, Any]
    error_code: Optional[str]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkflowRunDetailResponse(WorkflowRunResponse):
    steps: list[WorkflowStepResponse] = []


class TriggerWorkflowResponse(BaseModel):
    run_id: uuid.UUID
    status: str
    stream_url: str


class WorkflowRunListResponse(BaseModel):
    items: list[WorkflowRunResponse]
    total: int
    skip: int
    limit: int
