"""
WorkflowState — shared LangGraph state for all FoundrAI module graphs.

This TypedDict is the single source of truth for what data flows between
nodes in a workflow run.  Every node receives the full state and returns
a dict containing only the keys it modifies.

Instantiation example (WorkflowService):

    state: WorkflowState = {
        "project_id": str(project.id),
        "module_key": "idea_validation",
        "run_id": str(run.id),
        "agent_id": "idea_validator",
        "inputs": {
            "project_name": project.name,
            "idea_brief": project.idea_brief,
            "industry": project.industry,
        },
        "required_artifacts": {},   # pre-loaded by WorkflowService
        "retrieved_chunks": [],
        "current_draft": None,
        "parsed_output": None,
        "errors": [],
        "retry_count": 0,
        "steps_metadata": [],
        "persist_callback": my_async_callable,
        "session": db_session,
    }
"""

from __future__ import annotations

from typing import Any, Optional, TypedDict


class WorkflowState(TypedDict, total=False):
    """Typed state dict threaded through every LangGraph node.

    ``total=False`` means all keys are optional — this matches the LangGraph
    pattern where each node returns only a partial dict of updated keys.
    """

    # ── Identity ──────────────────────────────────────────────────────────
    project_id: str        # UUID string of the owning project
    module_key: str        # e.g. "idea_validation", "market_analysis"
    run_id: str            # UUID string of the workflow_run row
    agent_id: str          # e.g. "idea_validator", "market_researcher"

    # ── Inputs ────────────────────────────────────────────────────────────
    inputs: dict[str, Any]
    """Runtime inputs: project_name, idea_brief, industry, user_instructions, etc.
    Pre-populated by WorkflowService before the graph starts."""

    required_artifacts: dict[str, Any]
    """Upstream artifact content keyed by artifact_type.
    Pre-loaded by WorkflowService based on module dependency graph."""

    # ── RAG ───────────────────────────────────────────────────────────────
    retrieved_chunks: list[dict[str, Any]]
    """Chunks returned by the rag_node.
    Each dict: {chunk_id, content_text, score, source_type, module_key}."""

    # ── Generation ────────────────────────────────────────────────────────
    current_draft: Optional[str]
    """Raw LLM output string (pre-parse) set by generation_node."""

    parsed_output: Optional[dict]
    """Validated and parsed JSON dict set by the parse/validate node."""

    # ── Control flow ──────────────────────────────────────────────────────
    errors: list[str]
    """Accumulated validation / parse errors across retries."""

    retry_count: int
    """Number of repair retries attempted so far (0 = no retries yet)."""

    steps_metadata: list[dict]
    """Ordered step records: [{step_key, started_at, completed_at, metadata}].
    Each node appends its own record."""

    # ── Runtime objects (not serialized) ─────────────────────────────────
    persist_callback: Optional[Any]
    """Async callable(artifact_type, content_json, content_markdown) → None.
    Injected by WorkflowService; not serialized to DB."""

    session: Optional[Any]
    """SQLAlchemy AsyncSession for DB access within nodes.
    Injected by WorkflowService; not serialized to DB."""


def make_initial_state(**kwargs: Any) -> WorkflowState:
    """
    Create a WorkflowState with safe defaults for all fields.

    Keyword arguments override the defaults.

    Example::

        state = make_initial_state(
            project_id="abc123",
            module_key="idea_validation",
        )
    """
    defaults: WorkflowState = {
        # Identity — empty strings; callers must supply real values
        "project_id": "",
        "module_key": "",
        "run_id": "",
        "agent_id": "",
        # Inputs — empty dicts
        "inputs": {},
        "required_artifacts": {},
        # RAG — empty list
        "retrieved_chunks": [],
        # Generation — None
        "current_draft": None,
        "parsed_output": None,
        # Control flow — empty / zero
        "errors": [],
        "retry_count": 0,
        "steps_metadata": [],
        # Runtime — None (not serialized)
        "persist_callback": None,
        "session": None,
    }
    defaults.update(kwargs)  # type: ignore[typeddict-item]
    return defaults
