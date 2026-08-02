"""
ProjectRepository — all database access for projects and project_modules tables.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project
from app.models.project_module import ProjectModule


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Project CRUD ──────────────────────────────────────────────────────

    async def create(
        self,
        user_id: uuid.UUID,
        name: str,
        idea_brief: str,
        tagline: str | None = None,
        industry: str | None = None,
    ) -> Project:
        """Persist a new project (no modules yet — caller seeds them)."""
        project = Project(
            user_id=user_id,
            name=name,
            idea_brief=idea_brief,
            tagline=tagline,
            industry=industry,
        )
        self._session.add(project)
        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def get_by_id(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        include_modules: bool = False,
    ) -> Optional[Project]:
        """
        Return a project owned by user_id, or None.
        Soft-deleted projects are never returned.
        """
        stmt = select(Project).where(
            Project.id == project_id,
            Project.user_id == user_id,
            Project.deleted_at.is_(None),
        )
        if include_modules:
            stmt = stmt.options(selectinload(Project.modules))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
        include_modules: bool = False,
    ) -> list[Project]:
        """Return paginated projects for a user, newest first."""
        stmt = (
            select(Project)
            .where(Project.user_id == user_id, Project.deleted_at.is_(None))
            .order_by(Project.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if include_modules:
            stmt = stmt.options(selectinload(Project.modules))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(self, user_id: uuid.UUID) -> int:
        """Count non-deleted projects for a user."""
        from sqlalchemy import func
        result = await self._session.execute(
            select(func.count(Project.id)).where(
                Project.user_id == user_id,
                Project.deleted_at.is_(None),
            )
        )
        return result.scalar_one()

    async def update(
        self,
        project: Project,
        name: str | None = None,
        tagline: str | None = None,
        idea_brief: str | None = None,
        industry: str | None = None,
        stage: str | None = None,
    ) -> Project:
        """Apply partial updates to a project."""
        if name is not None:
            project.name = name
        if tagline is not None:
            project.tagline = tagline
        if idea_brief is not None:
            project.idea_brief = idea_brief
        if industry is not None:
            project.industry = industry
        if stage is not None:
            project.stage = stage
        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def soft_delete(self, project: Project) -> None:
        """Soft-delete: set deleted_at timestamp."""
        from datetime import datetime, timezone
        project.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

    # ── Module access ─────────────────────────────────────────────────────

    async def get_module(
        self,
        project_id: uuid.UUID,
        module_key: str,
    ) -> Optional[ProjectModule]:
        """Return a specific module for a project."""
        result = await self._session.execute(
            select(ProjectModule).where(
                ProjectModule.project_id == project_id,
                ProjectModule.module_key == module_key,
            )
        )
        return result.scalar_one_or_none()

    async def get_modules(self, project_id: uuid.UUID) -> list[ProjectModule]:
        """Return all modules for a project, sorted by sort_order."""
        result = await self._session.execute(
            select(ProjectModule)
            .where(ProjectModule.project_id == project_id)
            .order_by(ProjectModule.sort_order)
        )
        return list(result.scalars().all())

    async def bulk_create_modules(
        self, modules: list[ProjectModule]
    ) -> list[ProjectModule]:
        """Persist multiple module records in one flush."""
        for mod in modules:
            self._session.add(mod)
        await self._session.flush()
        return modules
