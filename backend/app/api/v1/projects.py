"""
Projects and Modules API endpoints — /api/v1/projects/*

POST   /projects                              → 201  Create project (seeds 8 modules)
GET    /projects                              → 200  Paginated project list
GET    /projects/{id}                         → 200  Project with modules
PATCH  /projects/{id}                         → 200  Partial update
DELETE /projects/{id}                         → 204  Soft delete
GET    /projects/{id}/modules                 → 200  All modules for project
GET    /projects/{id}/modules/{module_key}    → 200  Single module with dependency info
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.constants import MODULE_DEPENDENCIES
from app.core.exceptions import ModuleNotFoundError
from app.database.session import get_db
from app.models.user import User
from app.schemas.project import (
    CreateProjectRequest,
    ProjectListResponse,
    ProjectModuleResponse,
    ProjectWithModulesResponse,
    UpdateProjectRequest,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


# ── Project endpoints ──────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=ProjectWithModulesResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
)
async def create_project(
    body: CreateProjectRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> ProjectWithModulesResponse:
    """
    Create a project and seed 8 workflow modules.
    The first module (idea_validation) is immediately available.
    All others start locked until their dependencies are completed.
    """
    svc = ProjectService(session)
    return await svc.create_project(user_id=current_user.id, data=body)


@router.get(
    "",
    response_model=ProjectListResponse,
    status_code=status.HTTP_200_OK,
    summary="List projects",
)
async def list_projects(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> ProjectListResponse:
    """Return paginated list of projects owned by the authenticated user."""
    svc = ProjectService(session)
    return await svc.list_projects(user_id=current_user.id, skip=skip, limit=limit)


@router.get(
    "/{project_id}",
    response_model=ProjectWithModulesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project with modules",
)
async def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> ProjectWithModulesResponse:
    """Return a project with all its modules. Returns 404 if not found or not owned."""
    svc = ProjectService(session)
    return await svc.get_project(project_id=project_id, user_id=current_user.id)


@router.patch(
    "/{project_id}",
    response_model=ProjectWithModulesResponse,
    status_code=status.HTTP_200_OK,
    summary="Update project",
)
async def update_project(
    project_id: uuid.UUID,
    body: UpdateProjectRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> ProjectWithModulesResponse:
    """Partially update a project. Returns 404 if not found or not owned."""
    svc = ProjectService(session)
    return await svc.update_project(
        project_id=project_id, user_id=current_user.id, data=body
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
)
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete a project. Returns 404 if not found or not owned."""
    svc = ProjectService(session)
    await svc.delete_project(project_id=project_id, user_id=current_user.id)


# ── Module endpoints ───────────────────────────────────────────────────────────

@router.get(
    "/{project_id}/modules",
    response_model=list[ProjectModuleResponse],
    status_code=status.HTTP_200_OK,
    summary="List modules for a project",
)
async def list_modules(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> list[ProjectModuleResponse]:
    """
    Return all 8 modules for a project, sorted by sort_order.
    Returns 404 if the project is not found or not owned.
    """
    svc = ProjectService(session)
    # Verify ownership via get_project (raises ProjectNotFoundError if wrong)
    project = await svc.get_project(project_id=project_id, user_id=current_user.id)
    return project.modules


@router.get(
    "/{project_id}/modules/{module_key}",
    response_model=ProjectModuleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific module",
)
async def get_module(
    project_id: uuid.UUID,
    module_key: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> ProjectModuleResponse:
    """
    Return a single module with its current status.
    Returns 404 if the project or module is not found.
    """
    svc = ProjectService(session)
    # Verify project ownership
    project = await svc.get_project(project_id=project_id, user_id=current_user.id)

    module = next(
        (m for m in project.modules if m.module_key == module_key), None
    )
    if module is None:
        raise ModuleNotFoundError(module_key)

    return module
