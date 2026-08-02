"""
Integration tests for GraphFactory and execute_workflow background task.

Test matrix
-----------
test_graph_factory_get_all_modules       — all 8 keys return a CompiledGraph
test_graph_factory_get_unknown_raises    — unknown key raises ValueError
test_graph_factory_get_agent_id          — correct agent_id per module
test_graph_factory_compiles_cleanly      — compiled graphs have nodes
test_execute_workflow_marks_completed    — mocked ainvoke → completed status
test_execute_workflow_marks_failed       — mocked ainvoke raises → failed status
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.base import Base
import app.models  # noqa: F401 — register all ORM models

# ── DB fixture ────────────────────────────────────────────────────────────────

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_session_and_factory():
    """
    Yield (AsyncSession, async_sessionmaker) backed by in-memory SQLite.
    Tables are created fresh for each test.
    """
    engine = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with factory() as session:
        yield session, factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _create_user_and_project(session: AsyncSession) -> tuple[uuid.UUID, uuid.UUID]:
    """Seed a user + project, return (user_id, project_id)."""
    from app.models.user import User
    from app.models.project import Project
    from app.models.project_module import ProjectModule
    from app.core.constants import MODULE_KEYS, MODULE_SORT_ORDER, MODULE_DISPLAY_NAMES

    user = User(
        email="runner@test.com",
        password_hash="$2b$12$fakehash_for_testing_only",
        full_name="Runner",
    )
    session.add(user)
    await session.flush()

    project = Project(
        user_id=user.id,
        name="Test Project",
        idea_brief="A brief idea description for testing.",
    )
    session.add(project)
    await session.flush()

    # Seed modules so WorkflowService can update module status
    for key in MODULE_KEYS:
        session.add(ProjectModule(
            project_id=project.id,
            module_key=key,
            display_name=MODULE_DISPLAY_NAMES[key],
            status="available",
            sort_order=MODULE_SORT_ORDER[key],
        ))
    await session.flush()

    return user.id, project.id


async def _create_run(
    session: AsyncSession,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    module_key: str = "idea_validation",
) -> uuid.UUID:
    """Trigger a workflow run via WorkflowService and return its run_id."""
    from app.services.workflow_service import WorkflowService
    svc = WorkflowService(session)
    resp = await svc.trigger(
        project_id=project_id,
        module_key=module_key,
        user_id=user_id,
    )
    await session.commit()
    return resp.run_id


# ── GraphFactory tests ────────────────────────────────────────────────────────

ALL_MODULE_KEYS = [
    "idea_validation",
    "market_research",
    "business_model",
    "product_strategy",
    "technical_architecture",
    "financial_planning",
    "marketing_strategy",
    "investor_documentation",
]

EXPECTED_AGENT_IDS = {
    "idea_validation": "idea_validator",
    "market_research": "market_researcher",
    "business_model": "business_modeler",
    "product_strategy": "product_strategist",
    "technical_architecture": "technical_architect",
    "financial_planning": "financial_analyst",
    "marketing_strategy": "marketing_strategist",
    "investor_documentation": "investor_writer",
}


def test_graph_factory_get_all_modules():
    """All 8 module keys should return a compiled graph without raising."""
    from ai.graphs.graph_factory import GraphFactory
    from langgraph.graph.graph import CompiledGraph

    for key in ALL_MODULE_KEYS:
        graph = GraphFactory.get_graph(key)
        assert graph is not None, f"get_graph({key!r}) returned None"
        assert isinstance(graph, CompiledGraph), (
            f"Expected CompiledGraph for {key!r}, got {type(graph)}"
        )


def test_graph_factory_get_unknown_raises():
    """Unknown module_key should raise ValueError."""
    from ai.graphs.graph_factory import GraphFactory

    with pytest.raises(ValueError, match="Unknown module_key"):
        GraphFactory.get_graph("nonexistent_module")


def test_graph_factory_get_agent_id():
    """get_agent_id should return the correct agent_id for every module."""
    from ai.graphs.graph_factory import GraphFactory

    for module_key, expected_agent_id in EXPECTED_AGENT_IDS.items():
        result = GraphFactory.get_agent_id(module_key)
        assert result == expected_agent_id, (
            f"get_agent_id({module_key!r}) = {result!r}, expected {expected_agent_id!r}"
        )


def test_graph_factory_get_agent_id_unknown_raises():
    """get_agent_id with unknown key should also raise ValueError."""
    from ai.graphs.graph_factory import GraphFactory

    with pytest.raises(ValueError, match="Unknown module_key"):
        GraphFactory.get_agent_id("nonexistent_module")


def test_graph_factory_compiles_cleanly():
    """Compiled graphs should have a non-empty nodes dict."""
    from ai.graphs.graph_factory import GraphFactory

    for key in ALL_MODULE_KEYS:
        graph = GraphFactory.get_graph(key)
        # LangGraph compiled graphs expose their underlying graph nodes
        nodes = graph.get_graph().nodes
        assert len(nodes) > 0, f"Compiled graph for {key!r} has no nodes"


def test_graph_factory_caches_graphs():
    """Calling get_graph twice should return the same object (cache hit)."""
    from ai.graphs.graph_factory import GraphFactory

    g1 = GraphFactory.get_graph("idea_validation")
    g2 = GraphFactory.get_graph("idea_validation")
    assert g1 is g2, "GraphFactory should return the same cached instance"


# ── execute_workflow tests ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_execute_workflow_marks_completed_on_success(db_session_and_factory):
    """
    When the graph ainvoke returns a state with parsed_output set,
    the run status should be updated to 'completed'.
    """
    session, factory = db_session_and_factory
    user_id, project_id = await _create_user_and_project(session)
    run_id = await _create_run(session, project_id, user_id)

    # Mock GraphFactory.get_graph to return a compiled graph whose ainvoke
    # returns a state with parsed_output populated.
    mock_result_state = {
        "parsed_output": {"score": 85, "summary": "Great idea"},
        "errors": [],
    }
    mock_compiled = MagicMock()
    mock_compiled.ainvoke = AsyncMock(return_value=mock_result_state)

    with patch("app.background.workflow_runner.GraphFactory") as mock_factory:
        mock_factory.get_graph.return_value = mock_compiled
        mock_factory.get_agent_id.return_value = "idea_validator"

        from app.background.workflow_runner import execute_workflow
        await execute_workflow(
            project_id=project_id,
            module_key="idea_validation",
            run_id=run_id,
            user_id=user_id,
            session_factory=factory,
        )

    # Verify the run was marked completed
    from app.models.workflow_run import WorkflowRun
    async with factory() as verify_session:
        result = await verify_session.execute(
            select(WorkflowRun).where(WorkflowRun.id == run_id)
        )
        run = result.scalar_one_or_none()
        assert run is not None
        assert run.status == "completed", (
            f"Expected 'completed', got {run.status!r}"
        )


@pytest.mark.asyncio
async def test_execute_workflow_marks_failed_on_error(db_session_and_factory):
    """
    When the graph ainvoke raises an exception,
    the run status should be updated to 'failed'.
    """
    session, factory = db_session_and_factory
    user_id, project_id = await _create_user_and_project(session)
    run_id = await _create_run(session, project_id, user_id)

    mock_compiled = MagicMock()
    mock_compiled.ainvoke = AsyncMock(side_effect=RuntimeError("Ollama connection failed"))

    with patch("app.background.workflow_runner.GraphFactory") as mock_factory:
        mock_factory.get_graph.return_value = mock_compiled
        mock_factory.get_agent_id.return_value = "idea_validator"

        from app.background.workflow_runner import execute_workflow
        # execute_workflow should NOT raise — it handles exceptions internally
        await execute_workflow(
            project_id=project_id,
            module_key="idea_validation",
            run_id=run_id,
            user_id=user_id,
            session_factory=factory,
        )

    # Verify the run was marked failed
    from app.models.workflow_run import WorkflowRun
    async with factory() as verify_session:
        result = await verify_session.execute(
            select(WorkflowRun).where(WorkflowRun.id == run_id)
        )
        run = result.scalar_one_or_none()
        assert run is not None
        assert run.status == "failed", (
            f"Expected 'failed', got {run.status!r}"
        )
