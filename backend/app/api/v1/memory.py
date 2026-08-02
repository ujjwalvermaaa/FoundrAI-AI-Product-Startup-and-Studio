"""
Memory search API endpoint.

POST /projects/{project_id}/memory/search — semantic search over indexed project memory.
"""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ai.memory.memory_manager import MemoryManager
from app.api.deps import get_current_active_user
from app.core.exceptions import ProjectNotFoundError
from app.database.session import get_db
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.schemas.memory import MemorySearchRequest, MemorySearchResponse, MemorySearchResultItem

router = APIRouter(prefix="/projects", tags=["Memory"])


@router.post(
    "/{project_id}/memory/search",
    response_model=MemorySearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search project memory",
)
async def search_memory(
    project_id: uuid.UUID,
    body: MemorySearchRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> MemorySearchResponse:
    """
    Semantically search indexed memory chunks for the given project.

    Returns 404 if the project is not found or not owned by the current user.
    Returns empty results if no content has been indexed yet.
    """
    # Validate project ownership
    project_repo = ProjectRepository(session)
    project = await project_repo.get_by_id(
        project_id=project_id, user_id=current_user.id
    )
    if not project:
        raise ProjectNotFoundError(str(project_id))

    manager = MemoryManager()
    try:
        raw_results = await manager.search(
            project_id=str(project_id),
            query=body.query,
            top_k=body.top_k,
            session=session,
        )
    except Exception:
        # If search fails (e.g., no FAISS index), return empty results
        raw_results = []

    items = [
        MemorySearchResultItem(
            chunk_id=r.chunk_id,
            content_text=r.content_text,
            score=r.score,
            source_type=r.source_type,
            source_id=r.source_id,
            module_key=r.module_key,
            metadata=r.metadata,
        )
        for r in raw_results
    ]

    return MemorySearchResponse(results=items, total=len(items))
