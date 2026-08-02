"""
ProjectService — business logic for project CRUD and module management.

Key responsibility: when a project is created, exactly 8 ProjectModule
records are seeded. The first module (idea_validation) starts as
'available'; all others start as 'locked'.
"""

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    MODULE_DISPLAY_NAMES,
    MODULE_KEYS,
    MODULE_SORT_ORDER,
    MODULE_STATUS_AVAILABLE,
    MODULE_STATUS_LOCKED,
)
from app.core.exceptions import ProjectNotFoundError
from app.models.project import Project
from app.models.project_module import ProjectModule
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import (
    CreateProjectRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectWithModulesResponse,
    UpdateProjectRequest,
)

logger = logging.getLogger(__name__)


def _seed_modules(project_id: uuid.UUID) -> list[ProjectModule]:
    """
    Build the 8 ProjectModule instances for a new project.
    Only the first module (idea_validation) is immediately available.
    """
    modules: list[ProjectModule] = []
    for key in MODULE_KEYS:
        status = MODULE_STATUS_AVAILABLE if key == MODULE_KEYS[0] else MODULE_STATUS_LOCKED
        modules.append(
            ProjectModule(
                project_id=project_id,
                module_key=key,
                display_name=MODULE_DISPLAY_NAMES[key],
                status=status,
                sort_order=MODULE_SORT_ORDER[key],
            )
        )
    return modules


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = ProjectRepository(session)

        from ai.memory.memory_manager import MemoryManager
        self._memory_manager = MemoryManager()

    async def create_project(
        self,
        user_id: uuid.UUID,
        data: CreateProjectRequest,
    ) -> ProjectWithModulesResponse:
        """
        Create a project and seed 8 modules.
        Returns the project with all modules attached.
        """
        project = await self._repo.create(
            user_id=user_id,
            name=data.name,
            idea_brief=data.idea_brief,
            tagline=data.tagline,
            industry=data.industry,
        )

        modules = _seed_modules(project.id)
        await self._repo.bulk_create_modules(modules)

        # Reload with modules relationship populated
        project_with_modules = await self._repo.get_by_id(
            project_id=project.id,
            user_id=user_id,
            include_modules=True,
        )
        assert project_with_modules is not None  # just created — must exist
        result = ProjectWithModulesResponse.model_validate(project_with_modules)

        # Fire-and-continue: write audit log
        try:
            from app.repositories.audit_repository import AuditRepository
            audit_repo = AuditRepository()
            await audit_repo.create(
                session=self._session,
                event_type="project.create",
                user_id=user_id,
                resource_type="project",
                resource_id=project.id,
                metadata={"project_name": project.name},
            )
        except Exception as exc:
            logger.warning("Audit log failed for project.create: %s", exc)

        # Fire-and-continue: index project brief into memory
        if data.idea_brief:
            try:
                await self._memory_manager.index_brief(
                    project_id=str(project.id),
                    brief_text=data.idea_brief,
                    session=self._session,
                )
            except Exception as exc:
                logger.warning(
                    "Memory index_brief failed for project %s: %s",
                    project.id, exc,
                )

        return result

    async def get_project(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ProjectWithModulesResponse:
        """
        Return a project with its modules.
        Raises ProjectNotFoundError if not found or not owned by user.
        """
        project = await self._repo.get_by_id(
            project_id=project_id,
            user_id=user_id,
            include_modules=True,
        )
        if not project:
            raise ProjectNotFoundError(str(project_id))
        return ProjectWithModulesResponse.model_validate(project)

    async def list_projects(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> ProjectListResponse:
        """Return paginated project list for a user, including modules."""
        projects = await self._repo.list_by_user(
            user_id=user_id, skip=skip, limit=limit, include_modules=True
        )
        total = await self._repo.count_by_user(user_id=user_id)
        return ProjectListResponse(
            items=[ProjectWithModulesResponse.model_validate(p) for p in projects],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update_project(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        data: UpdateProjectRequest,
    ) -> ProjectWithModulesResponse:
        """
        Partially update a project.
        Raises ProjectNotFoundError if not found or not owned by user.
        """
        project = await self._repo.get_by_id(
            project_id=project_id,
            user_id=user_id,
            include_modules=True,
        )
        if not project:
            raise ProjectNotFoundError(str(project_id))

        await self._repo.update(
            project=project,
            name=data.name,
            tagline=data.tagline,
            idea_brief=data.idea_brief,
            industry=data.industry,
            stage=data.stage,
        )
        # Refresh the project object to get updated_at
        updated = await self._repo.get_by_id(
            project_id=project_id,
            user_id=user_id,
            include_modules=True,
        )
        assert updated is not None
        result = ProjectWithModulesResponse.model_validate(updated)

        # Fire-and-continue: re-index brief if it was updated
        if data.idea_brief is not None:
            try:
                await self._memory_manager.index_brief(
                    project_id=str(project_id),
                    brief_text=data.idea_brief,
                    session=self._session,
                )
            except Exception as exc:
                logger.warning(
                    "Memory index_brief failed on update for project %s: %s",
                    project_id, exc,
                )

        return result

    async def delete_project(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        """
        Soft-delete a project.
        Raises ProjectNotFoundError if not found or not owned by user.
        """
        project = await self._repo.get_by_id(
            project_id=project_id,
            user_id=user_id,
        )
        if not project:
            raise ProjectNotFoundError(str(project_id))
        await self._repo.soft_delete(project)
