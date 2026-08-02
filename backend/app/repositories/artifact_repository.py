"""
ArtifactRepository — all database access for artifacts and artifact_versions.
"""

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.artifact import Artifact
from app.models.artifact_version import ArtifactVersion


class ArtifactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Artifact CRUD ─────────────────────────────────────────────────────

    async def get_by_project_and_type(
        self,
        project_id: uuid.UUID,
        artifact_type: str,
    ) -> Optional[Artifact]:
        """Return an artifact by project + type, or None."""
        result = await self._session.execute(
            select(Artifact).where(
                Artifact.project_id == project_id,
                Artifact.artifact_type == artifact_type,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        artifact_id: uuid.UUID,
        project_id: uuid.UUID,
    ) -> Optional[Artifact]:
        """Return an artifact by id within a project, or None."""
        result = await self._session.execute(
            select(Artifact).where(
                Artifact.id == artifact_id,
                Artifact.project_id == project_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Artifact]:
        """Return paginated artifacts for a project, ordered by updated_at desc."""
        result = await self._session.execute(
            select(Artifact)
            .where(Artifact.project_id == project_id)
            .order_by(Artifact.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_project(self, project_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count(Artifact.id)).where(Artifact.project_id == project_id)
        )
        return result.scalar_one()

    async def create(
        self,
        project_id: uuid.UUID,
        module_key: str,
        artifact_type: str,
        title: str,
        content_json: dict,
        content_markdown: str | None = None,
        source: str = "ai",
        workflow_run_id: uuid.UUID | None = None,
    ) -> Artifact:
        """Create a new artifact record (version is created separately)."""
        artifact = Artifact(
            project_id=project_id,
            module_key=module_key,
            artifact_type=artifact_type,
            title=title,
            content_json=content_json,
            content_markdown=content_markdown,
            source=source,
            workflow_run_id=workflow_run_id,
        )
        self._session.add(artifact)
        await self._session.flush()
        await self._session.refresh(artifact)
        return artifact

    async def update_content(
        self,
        artifact: Artifact,
        content_json: dict,
        content_markdown: str | None,
        current_version_id: uuid.UUID,
        source: str = "user",
    ) -> Artifact:
        """Update artifact content and point current_version_id to the new version."""
        artifact.content_json = content_json
        artifact.content_markdown = content_markdown
        artifact.current_version_id = current_version_id
        artifact.source = source
        await self._session.flush()
        await self._session.refresh(artifact)
        return artifact

    async def set_current_version(
        self, artifact: Artifact, version_id: uuid.UUID
    ) -> None:
        """Point artifact.current_version_id to the given version."""
        artifact.current_version_id = version_id
        await self._session.flush()

    # ── Version CRUD ──────────────────────────────────────────────────────

    async def get_next_version_number(self, artifact_id: uuid.UUID) -> int:
        """Return max(version_number) + 1 for an artifact (1 if none exist)."""
        result = await self._session.execute(
            select(func.max(ArtifactVersion.version_number)).where(
                ArtifactVersion.artifact_id == artifact_id
            )
        )
        current_max = result.scalar_one_or_none()
        return (current_max or 0) + 1

    async def create_version(
        self,
        artifact_id: uuid.UUID,
        content_json: dict,
        content_markdown: str | None = None,
        change_summary: str | None = None,
        created_by: str = "ai",
    ) -> ArtifactVersion:
        """Create a new version record with auto-incrementing version_number."""
        version_number = await self.get_next_version_number(artifact_id)
        version = ArtifactVersion(
            artifact_id=artifact_id,
            version_number=version_number,
            content_json=content_json,
            content_markdown=content_markdown,
            change_summary=change_summary,
            created_by=created_by,
        )
        self._session.add(version)
        await self._session.flush()
        await self._session.refresh(version)
        return version

    async def get_versions(
        self,
        artifact_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ArtifactVersion]:
        """Return all versions for an artifact, newest first."""
        result = await self._session.execute(
            select(ArtifactVersion)
            .where(ArtifactVersion.artifact_id == artifact_id)
            .order_by(ArtifactVersion.version_number.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_version_by_number(
        self,
        artifact_id: uuid.UUID,
        version_number: int,
    ) -> Optional[ArtifactVersion]:
        """Return a specific version snapshot."""
        result = await self._session.execute(
            select(ArtifactVersion).where(
                ArtifactVersion.artifact_id == artifact_id,
                ArtifactVersion.version_number == version_number,
            )
        )
        return result.scalar_one_or_none()
