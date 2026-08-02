"""
Export API endpoints — /api/v1/projects/{project_id}/export/*

POST /projects/{id}/export/investor-pack          → 200  Generate investor pack
GET  /projects/{id}/export/investor-pack/download → 200  Download latest export file
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.config import settings
from app.core.exceptions import InsufficientArtifactsError, ProjectNotFoundError
from app.database.session import get_db
from app.exporters.investor_pack import generate_investor_pack
from app.models.user import User
from app.repositories.project_repository import ProjectRepository

router = APIRouter(prefix="/projects", tags=["Export"])


# ── POST /export/investor-pack ────────────────────────────────────────────────

@router.post(
    "/{project_id}/export/investor-pack",
    status_code=status.HTTP_200_OK,
    summary="Generate investor pack markdown export",
)
async def export_investor_pack(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """
    Generate a structured markdown investor pack from all available artifacts.

    - Returns 409 INSUFFICIENT_ARTIFACTS if validation_report, business_model_canvas,
      or financial_model are missing.
    - Returns 200 with file path and download URL on success.
    """
    # Verify ownership
    project_repo = ProjectRepository(session)
    project = await project_repo.get_by_id(
        project_id=project_id,
        user_id=current_user.id,
    )
    if not project:
        raise ProjectNotFoundError(str(project_id))

    export_dir = os.path.abspath(settings.export_dir)
    file_path = await generate_investor_pack(
        project_id=project_id,
        project_name=project.name,
        idea_brief=project.idea_brief,
        session=session,
        export_dir=export_dir,
    )

    filename = Path(file_path).name
    download_url = f"/api/v1/projects/{project_id}/export/investor-pack/download"

    return {
        "file_path": file_path,
        "download_url": download_url,
        "filename": filename,
    }


# ── GET /export/investor-pack/download ───────────────────────────────────────

@router.get(
    "/{project_id}/export/investor-pack/download",
    summary="Download the latest investor pack export",
)
async def download_investor_pack(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> FileResponse:
    """
    Return the most recently generated investor pack file for download.
    Returns 404 if no export file exists yet.
    """
    # Verify ownership
    project_repo = ProjectRepository(session)
    project = await project_repo.get_by_id(
        project_id=project_id,
        user_id=current_user.id,
    )
    if not project:
        raise ProjectNotFoundError(str(project_id))

    export_dir = Path(os.path.abspath(settings.export_dir))
    prefix = str(project_id)

    # Find the most recent file for this project
    matching = sorted(
        [f for f in export_dir.glob(f"{prefix}_*.md")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not matching:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No export found for this project. Generate one first.")

    latest = matching[0]
    return FileResponse(
        path=str(latest),
        filename=latest.name,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{latest.name}"'},
    )
