"""
ArtifactService — business logic for artifact upsert, versioning, and retrieval.

Core design:
- Artifacts are keyed by (project_id, artifact_type) — one per type per project
- Every create or update produces a new ArtifactVersion with a monotonically
  increasing version_number
- The artifact's current_version_id always points to the latest version
- AI writes use source='ai'; user edits use source='user'
"""

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ArtifactNotFoundError, ProjectNotFoundError
from app.repositories.artifact_repository import ArtifactRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.artifact import (
    ArtifactListResponse,
    ArtifactResponse,
    ArtifactVersionResponse,
    ArtifactWithVersionsResponse,
    UpdateArtifactRequest,
)

logger = logging.getLogger(__name__)


class ArtifactService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = ArtifactRepository(session)
        self._project_repo = ProjectRepository(session)

        from ai.memory.memory_manager import MemoryManager
        self._memory_manager = MemoryManager()

    async def _assert_project_owned(
        self, project_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        """Raise ProjectNotFoundError if project not found or not owned by user."""
        project = await self._project_repo.get_by_id(
            project_id=project_id, user_id=user_id
        )
        if not project:
            raise ProjectNotFoundError(str(project_id))

    # ── Upsert (used by AI workflow to persist artifact) ───────────────────

    async def upsert_artifact(
        self,
        project_id: uuid.UUID,
        module_key: str,
        artifact_type: str,
        title: str,
        content_json: dict,
        content_markdown: str | None = None,
        source: str = "ai",
        workflow_run_id: uuid.UUID | None = None,
        change_summary: str | None = None,
    ) -> ArtifactResponse:
        """
        Create or update an artifact and always produce a new version.

        If the artifact (project_id, artifact_type) doesn't exist → creates it.
        If it exists → updates content and bumps the version.
        """
        existing = await self._repo.get_by_project_and_type(project_id, artifact_type)

        if existing is None:
            # Create new artifact
            artifact = await self._repo.create(
                project_id=project_id,
                module_key=module_key,
                artifact_type=artifact_type,
                title=title,
                content_json=content_json,
                content_markdown=content_markdown,
                source=source,
                workflow_run_id=workflow_run_id,
            )
        else:
            artifact = existing

        # Always create a new version
        version = await self._repo.create_version(
            artifact_id=artifact.id,
            content_json=content_json,
            content_markdown=content_markdown,
            change_summary=change_summary,
            created_by=source,
        )

        # Point artifact to the new current version and update content
        artifact.content_json = content_json
        artifact.content_markdown = content_markdown
        artifact.current_version_id = version.id
        artifact.source = source
        if workflow_run_id:
            artifact.workflow_run_id = workflow_run_id
        await self._session.flush()
        await self._session.refresh(artifact)

        result = ArtifactResponse.model_validate(artifact)

        # Fire-and-continue: index into memory (errors must not block main op)
        try:
            from ai.memory.artifact_memory import extract_text_from_artifact
            content_text = extract_text_from_artifact(content_json, artifact_type)
            await self._memory_manager.index_artifact(
                project_id=str(project_id),
                artifact_id=str(artifact.id),
                artifact_type=artifact_type,
                module_key=module_key,
                content_text=content_text,
                session=self._session,
            )
        except Exception as exc:
            logger.warning(
                "Memory indexing failed for artifact %s (project %s): %s",
                artifact.id, project_id, exc,
            )

        return result

    # ── User edit ─────────────────────────────────────────────────────────

    async def edit_artifact(
        self,
        project_id: uuid.UUID,
        artifact_id: uuid.UUID,
        user_id: uuid.UUID,
        data: UpdateArtifactRequest,
    ) -> ArtifactResponse:
        """
        User manually edits artifact content — creates a new version with source='user'.
        """
        await self._assert_project_owned(project_id, user_id)

        artifact = await self._repo.get_by_id(artifact_id, project_id)
        if not artifact:
            raise ArtifactNotFoundError(str(artifact_id))

        version = await self._repo.create_version(
            artifact_id=artifact.id,
            content_json=data.content_json,
            content_markdown=data.content_markdown,
            change_summary=data.change_summary,
            created_by="user",
        )

        updated = await self._repo.update_content(
            artifact=artifact,
            content_json=data.content_json,
            content_markdown=data.content_markdown,
            current_version_id=version.id,
            source="user",
        )
        result = ArtifactResponse.model_validate(updated)

        # Fire-and-continue: invalidate old chunks then re-index with new content
        try:
            from ai.memory.artifact_memory import extract_text_from_artifact
            await self._memory_manager.invalidate_artifact(
                project_id=str(project_id),
                artifact_id=str(artifact.id),
                session=self._session,
            )
            content_text = extract_text_from_artifact(
                data.content_json, artifact.artifact_type
            )
            await self._memory_manager.index_artifact(
                project_id=str(project_id),
                artifact_id=str(artifact.id),
                artifact_type=artifact.artifact_type,
                module_key=artifact.module_key,
                content_text=content_text,
                session=self._session,
            )
        except Exception as exc:
            logger.warning(
                "Memory re-indexing failed for artifact %s (project %s): %s",
                artifact.id, project_id, exc,
            )

        return result

    # ── Read ──────────────────────────────────────────────────────────────

    async def list_artifacts(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> ArtifactListResponse:
        await self._assert_project_owned(project_id, user_id)
        artifacts = await self._repo.list_by_project(project_id, skip, limit)
        total = await self._repo.count_by_project(project_id)
        return ArtifactListResponse(
            items=[ArtifactResponse.model_validate(a) for a in artifacts],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_artifact(
        self,
        project_id: uuid.UUID,
        artifact_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ArtifactResponse:
        await self._assert_project_owned(project_id, user_id)
        artifact = await self._repo.get_by_id(artifact_id, project_id)
        if not artifact:
            raise ArtifactNotFoundError(str(artifact_id))
        return ArtifactResponse.model_validate(artifact)

    async def list_versions(
        self,
        project_id: uuid.UUID,
        artifact_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[ArtifactVersionResponse]:
        await self._assert_project_owned(project_id, user_id)
        artifact = await self._repo.get_by_id(artifact_id, project_id)
        if not artifact:
            raise ArtifactNotFoundError(str(artifact_id))
        versions = await self._repo.get_versions(artifact.id)
        return [ArtifactVersionResponse.model_validate(v) for v in versions]

    async def get_version(
        self,
        project_id: uuid.UUID,
        artifact_id: uuid.UUID,
        version_number: int,
        user_id: uuid.UUID,
    ) -> ArtifactVersionResponse:
        await self._assert_project_owned(project_id, user_id)
        artifact = await self._repo.get_by_id(artifact_id, project_id)
        if not artifact:
            raise ArtifactNotFoundError(str(artifact_id))
        version = await self._repo.get_version_by_number(artifact.id, version_number)
        if not version:
            raise ArtifactNotFoundError(f"Version {version_number} not found")
        return ArtifactVersionResponse.model_validate(version)
