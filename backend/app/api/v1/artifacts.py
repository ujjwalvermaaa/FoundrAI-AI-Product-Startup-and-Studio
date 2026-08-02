"""
Artifact API endpoints — /api/v1/projects/{project_id}/artifacts/*

GET    /projects/{pid}/artifacts                          → 200  Paginated list
GET    /projects/{pid}/artifacts/{aid}                    → 200  Full artifact
PATCH  /projects/{pid}/artifacts/{aid}                    → 200  User edit (new version)
GET    /projects/{pid}/artifacts/{aid}/versions           → 200  Version list
GET    /projects/{pid}/artifacts/{aid}/versions/{vnum}    → 200  Version snapshot
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.artifact import (
    ArtifactListResponse,
    ArtifactResponse,
    ArtifactVersionResponse,
    UpdateArtifactRequest,
)
from app.services.artifact_service import ArtifactService

router = APIRouter(
    prefix="/projects/{project_id}/artifacts",
    tags=["Artifacts"],
)


@router.get(
    "",
    response_model=ArtifactListResponse,
    status_code=status.HTTP_200_OK,
    summary="List artifacts for a project",
)
async def list_artifacts(
    project_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> ArtifactListResponse:
    """Return paginated artifacts for a project. 404 if project not owned."""
    svc = ArtifactService(session)
    return await svc.list_artifacts(
        project_id=project_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{artifact_id}",
    response_model=ArtifactResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single artifact",
)
async def get_artifact(
    project_id: uuid.UUID,
    artifact_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> ArtifactResponse:
    """Return a single artifact. 404 if not found or project not owned."""
    svc = ArtifactService(session)
    return await svc.get_artifact(
        project_id=project_id,
        artifact_id=artifact_id,
        user_id=current_user.id,
    )


@router.patch(
    "/{artifact_id}",
    response_model=ArtifactResponse,
    status_code=status.HTTP_200_OK,
    summary="Edit artifact content (creates new version)",
)
async def edit_artifact(
    project_id: uuid.UUID,
    artifact_id: uuid.UUID,
    body: UpdateArtifactRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> ArtifactResponse:
    """
    User edits an artifact. Creates a new version with source='user'.
    Returns SCHEMA_VALIDATION_FAILED (422) if content_json is invalid.
    """
    svc = ArtifactService(session)
    return await svc.edit_artifact(
        project_id=project_id,
        artifact_id=artifact_id,
        user_id=current_user.id,
        data=body,
    )


@router.get(
    "/{artifact_id}/versions",
    response_model=list[ArtifactVersionResponse],
    status_code=status.HTTP_200_OK,
    summary="List all versions of an artifact",
)
async def list_versions(
    project_id: uuid.UUID,
    artifact_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> list[ArtifactVersionResponse]:
    """Return all versions newest-first. 404 if artifact not found."""
    svc = ArtifactService(session)
    return await svc.list_versions(
        project_id=project_id,
        artifact_id=artifact_id,
        user_id=current_user.id,
    )


@router.get(
    "/{artifact_id}/versions/{version_number}",
    response_model=ArtifactVersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific version snapshot",
)
async def get_version(
    project_id: uuid.UUID,
    artifact_id: uuid.UUID,
    version_number: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> ArtifactVersionResponse:
    """Return a specific version snapshot by version number."""
    svc = ArtifactService(session)
    return await svc.get_version(
        project_id=project_id,
        artifact_id=artifact_id,
        version_number=version_number,
        user_id=current_user.id,
    )
