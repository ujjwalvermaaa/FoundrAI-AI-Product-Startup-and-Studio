"""
Unit tests for ProjectService — project CRUD and module seeding logic.
Uses in-memory SQLite via db_session fixture.
"""

import uuid

import pytest

from app.core.constants import (
    MODULE_KEYS,
    MODULE_STATUS_AVAILABLE,
    MODULE_STATUS_LOCKED,
)
from app.core.exceptions import ProjectNotFoundError
from app.schemas.project import CreateProjectRequest, UpdateProjectRequest
from app.services.project_service import ProjectService


def _make_user_id() -> uuid.UUID:
    return uuid.uuid4()


def _create_req(**kwargs) -> CreateProjectRequest:
    defaults = {
        "name": "Test Startup",
        "idea_brief": "A platform that connects coffee lovers with local roasters.",
        "tagline": "Find your perfect cup.",
        "industry": "Food & Beverage",
    }
    defaults.update(kwargs)
    return CreateProjectRequest(**defaults)


# ── Create ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_project_returns_project(db_session):
    user_id = _make_user_id()
    svc = ProjectService(db_session)
    result = await svc.create_project(user_id=user_id, data=_create_req())
    assert result.id is not None
    assert result.name == "Test Startup"
    assert result.user_id == user_id


@pytest.mark.asyncio
async def test_create_project_seeds_8_modules(db_session):
    svc = ProjectService(db_session)
    result = await svc.create_project(user_id=_make_user_id(), data=_create_req())
    assert len(result.modules) == 8


@pytest.mark.asyncio
async def test_create_project_module_keys_correct(db_session):
    svc = ProjectService(db_session)
    result = await svc.create_project(user_id=_make_user_id(), data=_create_req())
    keys = [m.module_key for m in result.modules]
    assert keys == MODULE_KEYS


@pytest.mark.asyncio
async def test_create_project_first_module_available(db_session):
    svc = ProjectService(db_session)
    result = await svc.create_project(user_id=_make_user_id(), data=_create_req())
    first = result.modules[0]
    assert first.module_key == "idea_validation"
    assert first.status == MODULE_STATUS_AVAILABLE


@pytest.mark.asyncio
async def test_create_project_remaining_modules_locked(db_session):
    svc = ProjectService(db_session)
    result = await svc.create_project(user_id=_make_user_id(), data=_create_req())
    for module in result.modules[1:]:
        assert module.status == MODULE_STATUS_LOCKED, (
            f"Module {module.module_key} should be locked but is {module.status}"
        )


@pytest.mark.asyncio
async def test_create_project_modules_sorted_by_sort_order(db_session):
    svc = ProjectService(db_session)
    result = await svc.create_project(user_id=_make_user_id(), data=_create_req())
    orders = [m.sort_order for m in result.modules]
    assert orders == sorted(orders)


# ── Get ───────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_project_found(db_session):
    user_id = _make_user_id()
    svc = ProjectService(db_session)
    created = await svc.create_project(user_id=user_id, data=_create_req())
    fetched = await svc.get_project(project_id=created.id, user_id=user_id)
    assert fetched.id == created.id
    assert len(fetched.modules) == 8


@pytest.mark.asyncio
async def test_get_project_not_found(db_session):
    svc = ProjectService(db_session)
    with pytest.raises(ProjectNotFoundError):
        await svc.get_project(project_id=uuid.uuid4(), user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_get_project_wrong_user_raises(db_session):
    """Ownership isolation: another user cannot see this project."""
    user_a = _make_user_id()
    user_b = _make_user_id()
    svc = ProjectService(db_session)
    created = await svc.create_project(user_id=user_a, data=_create_req())
    with pytest.raises(ProjectNotFoundError):
        await svc.get_project(project_id=created.id, user_id=user_b)


# ── List ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_projects_returns_user_projects(db_session):
    user_id = _make_user_id()
    svc = ProjectService(db_session)
    await svc.create_project(user_id=user_id, data=_create_req(name="P1"))
    await svc.create_project(user_id=user_id, data=_create_req(name="P2"))
    result = await svc.list_projects(user_id=user_id)
    assert result.total == 2
    assert len(result.items) == 2


@pytest.mark.asyncio
async def test_list_projects_isolates_users(db_session):
    user_a = _make_user_id()
    user_b = _make_user_id()
    svc = ProjectService(db_session)
    await svc.create_project(user_id=user_a, data=_create_req(name="A"))
    result = await svc.list_projects(user_id=user_b)
    assert result.total == 0


# ── Update ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_project_name(db_session):
    user_id = _make_user_id()
    svc = ProjectService(db_session)
    created = await svc.create_project(user_id=user_id, data=_create_req())
    updated = await svc.update_project(
        project_id=created.id,
        user_id=user_id,
        data=UpdateProjectRequest(name="New Name"),
    )
    assert updated.name == "New Name"
    assert updated.idea_brief == created.idea_brief  # unchanged


@pytest.mark.asyncio
async def test_update_project_wrong_user_raises(db_session):
    user_a = _make_user_id()
    svc = ProjectService(db_session)
    created = await svc.create_project(user_id=user_a, data=_create_req())
    with pytest.raises(ProjectNotFoundError):
        await svc.update_project(
            project_id=created.id,
            user_id=_make_user_id(),
            data=UpdateProjectRequest(name="Hack"),
        )


# ── Delete ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_soft_delete_hides_project(db_session):
    user_id = _make_user_id()
    svc = ProjectService(db_session)
    created = await svc.create_project(user_id=user_id, data=_create_req())
    await svc.delete_project(project_id=created.id, user_id=user_id)
    with pytest.raises(ProjectNotFoundError):
        await svc.get_project(project_id=created.id, user_id=user_id)


@pytest.mark.asyncio
async def test_soft_delete_excluded_from_list(db_session):
    user_id = _make_user_id()
    svc = ProjectService(db_session)
    p1 = await svc.create_project(user_id=user_id, data=_create_req(name="Keep"))
    p2 = await svc.create_project(user_id=user_id, data=_create_req(name="Delete"))
    await svc.delete_project(project_id=p2.id, user_id=user_id)
    result = await svc.list_projects(user_id=user_id)
    assert result.total == 1
    assert result.items[0].name == "Keep"


@pytest.mark.asyncio
async def test_delete_project_wrong_user_raises(db_session):
    user_a = _make_user_id()
    svc = ProjectService(db_session)
    created = await svc.create_project(user_id=user_a, data=_create_req())
    with pytest.raises(ProjectNotFoundError):
        await svc.delete_project(project_id=created.id, user_id=_make_user_id())
