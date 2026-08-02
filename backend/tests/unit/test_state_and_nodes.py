"""
Unit tests for Task 27: WorkflowState, base graph nodes, and PromptBuilder.

Tests:
  - test_workflow_state_has_required_fields
  - test_make_initial_state_has_safe_defaults
  - test_context_loader_adds_step_metadata
  - test_context_loader_returns_inputs_with_context_summary
  - test_rag_node_returns_empty_on_no_index
  - test_rag_node_adds_step_metadata
  - test_prompt_builder_returns_messages_list
  - test_prompt_builder_fills_project_name_placeholder
  - test_prompt_builder_fills_retrieved_context
  - test_prompt_builder_graceful_on_missing_template
  - test_prompt_builder_repair_includes_errors
"""

from __future__ import annotations

import numpy as np
import pytest

from ai.graphs.state import WorkflowState, make_initial_state


# ── WorkflowState tests ───────────────────────────────────────────────────────

def test_workflow_state_has_required_fields():
    """WorkflowState TypedDict must expose all required keys."""
    annotations = WorkflowState.__annotations__

    required_keys = [
        "project_id",
        "module_key",
        "run_id",
        "agent_id",
        "inputs",
        "required_artifacts",
        "retrieved_chunks",
        "current_draft",
        "parsed_output",
        "errors",
        "retry_count",
        "steps_metadata",
        "persist_callback",
        "session",
    ]
    for key in required_keys:
        assert key in annotations, f"WorkflowState missing field: {key}"


def test_make_initial_state_has_safe_defaults():
    """make_initial_state() must return a WorkflowState with safe, non-error defaults."""
    state = make_initial_state()

    # Identity strings default to empty
    assert state["project_id"] == ""
    assert state["module_key"] == ""
    assert state["run_id"] == ""
    assert state["agent_id"] == ""

    # Collections default to empty containers
    assert state["inputs"] == {}
    assert state["required_artifacts"] == {}
    assert state["retrieved_chunks"] == []
    assert state["errors"] == []
    assert state["steps_metadata"] == []

    # Numerics default to zero
    assert state["retry_count"] == 0

    # Optionals default to None
    assert state["current_draft"] is None
    assert state["parsed_output"] is None
    assert state["persist_callback"] is None
    assert state["session"] is None


def test_make_initial_state_accepts_overrides():
    """make_initial_state(**kwargs) should apply caller-provided overrides."""
    state = make_initial_state(project_id="proj-123", module_key="idea_validation")

    assert state["project_id"] == "proj-123"
    assert state["module_key"] == "idea_validation"
    # Unset fields should still have defaults
    assert state["retry_count"] == 0
    assert state["errors"] == []


# ── context_loader_node tests ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_context_loader_adds_step_metadata():
    """context_loader_node must append a step record with step_key='context_loader'."""
    from ai.graphs.nodes.context_loader import context_loader_node

    state = make_initial_state(
        project_id="test-project",
        module_key="idea_validation",
        inputs={
            "project_name": "TestCo",
            "idea_brief": "A great idea",
            "industry": "Tech",
        },
        required_artifacts={},
    )

    result = await context_loader_node(state)

    assert "steps_metadata" in result
    steps = result["steps_metadata"]
    assert len(steps) == 1
    step = steps[0]
    assert step["step_key"] == "context_loader"
    assert "started_at" in step
    assert "completed_at" in step
    assert "metadata" in step


@pytest.mark.asyncio
async def test_context_loader_returns_inputs_with_context_summary():
    """context_loader_node must enrich inputs with a context_summary key."""
    from ai.graphs.nodes.context_loader import context_loader_node

    state = make_initial_state(
        project_id="test-project",
        module_key="idea_validation",
        inputs={
            "project_name": "MyStartup",
            "idea_brief": "Disrupting the widget market",
            "industry": "SaaS",
        },
        required_artifacts={"prior_brief": {"some": "data"}},
    )

    result = await context_loader_node(state)

    assert "inputs" in result
    enriched = result["inputs"]
    assert "context_summary" in enriched
    assert "MyStartup" in enriched["context_summary"]
    # Original fields preserved
    assert enriched["project_name"] == "MyStartup"
    assert enriched["idea_brief"] == "Disrupting the widget market"


@pytest.mark.asyncio
async def test_context_loader_appends_to_existing_steps():
    """context_loader_node should append to already-existing steps_metadata."""
    from ai.graphs.nodes.context_loader import context_loader_node

    existing_step = {"step_key": "prior_step", "started_at": "x", "completed_at": "x", "metadata": {}}
    state = make_initial_state(
        project_id="p",
        inputs={"project_name": "X"},
        steps_metadata=[existing_step],
    )

    result = await context_loader_node(state)
    steps = result["steps_metadata"]
    assert len(steps) == 2
    assert steps[0]["step_key"] == "prior_step"
    assert steps[1]["step_key"] == "context_loader"


# ── rag_node tests ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rag_node_returns_empty_on_no_index():
    """rag_node must return an empty list when no FAISS index exists for the project."""
    from ai.graphs.nodes.rag_node import rag_node
    from ai.rag.retrieval import _set_embed_single

    # Inject a stub embed function to avoid loading sentence-transformers.
    # Since no FAISS index exists for "nonexistent-project-id", search returns [].
    def stub_embed(text: str) -> np.ndarray:
        return np.zeros(768, dtype=np.float32)

    _set_embed_single(stub_embed)
    try:
        state = make_initial_state(
            project_id="nonexistent-project-id-xyz",
            module_key="idea_validation",
            inputs={
                "project_name": "TestCo",
                "idea_brief": "A novel idea",
            },
        )
        result = await rag_node(state)
    finally:
        _set_embed_single(None)

    assert "retrieved_chunks" in result
    assert result["retrieved_chunks"] == []


@pytest.mark.asyncio
async def test_rag_node_adds_step_metadata():
    """rag_node must append a step record to steps_metadata."""
    from ai.graphs.nodes.rag_node import rag_node
    from ai.rag.retrieval import _set_embed_single

    def stub_embed(text: str) -> np.ndarray:
        return np.zeros(768, dtype=np.float32)

    _set_embed_single(stub_embed)
    try:
        state = make_initial_state(
            project_id="nonexistent-project-id-xyz",
            module_key="market_analysis",
            inputs={"idea_brief": "B2B SaaS analytics platform"},
        )
        result = await rag_node(state)
    finally:
        _set_embed_single(None)

    assert "steps_metadata" in result
    steps = result["steps_metadata"]
    assert len(steps) >= 1
    # Find the rag step
    rag_step = next((s for s in steps if "rag" in s.get("step_key", "").lower()), None)
    assert rag_step is not None, "No rag step found in steps_metadata"
    assert "started_at" in rag_step
    assert "completed_at" in rag_step


# ── PromptBuilder tests ───────────────────────────────────────────────────────

def test_prompt_builder_returns_messages_list():
    """PromptBuilder.build() must return a list of dicts with 'role' and 'content' keys."""
    from ai.runtime.prompt_builder import PromptBuilder

    builder = PromptBuilder()
    state = make_initial_state(
        agent_id="idea_validator",
        inputs={"project_name": "TestCo", "idea_brief": "Great idea", "industry": "Tech"},
    )
    messages, version = builder.build("idea_validator", state)

    assert isinstance(messages, list)
    assert len(messages) >= 2
    for msg in messages:
        assert "role" in msg
        assert "content" in msg
        assert isinstance(msg["content"], str)
    assert isinstance(version, str)


def test_prompt_builder_fills_project_name_placeholder():
    """PromptBuilder must substitute {project_name} from state inputs."""
    from pathlib import Path
    from ai.runtime.prompt_builder import PromptBuilder
    import tempfile, os

    # Create a temporary prompts directory with a user template containing {project_name}
    with tempfile.TemporaryDirectory() as tmpdir:
        agent_dir = Path(tmpdir) / "test_agent"
        agent_dir.mkdir()
        (agent_dir / "user.v1.md").write_text(
            "Analyse this project: {project_name} in {industry}.", encoding="utf-8"
        )

        builder = PromptBuilder(prompts_dir=Path(tmpdir))
        state = make_initial_state(
            agent_id="test_agent",
            inputs={
                "project_name": "WidgetWorld",
                "idea_brief": "Selling widgets online",
                "industry": "E-Commerce",
            },
        )
        messages, _ = builder.build("test_agent", state)

    # The user message should have the placeholder filled
    user_msg = next(m for m in messages if m["role"] == "user")
    assert "WidgetWorld" in user_msg["content"]
    assert "E-Commerce" in user_msg["content"]


def test_prompt_builder_fills_retrieved_context():
    """PromptBuilder context block must include retrieved chunk content."""
    from ai.runtime.prompt_builder import PromptBuilder

    builder = PromptBuilder()
    state = make_initial_state(
        inputs={"project_name": "X", "idea_brief": "Y", "industry": "Z"},
        retrieved_chunks=[
            {
                "chunk_id": "c1",
                "content_text": "Unique chunk content for testing ABC123",
                "score": 0.9,
                "source_type": "artifact",
                "module_key": "idea_validation",
            }
        ],
    )
    messages, _ = builder.build("some_agent", state)

    full_content = " ".join(m["content"] for m in messages)
    assert "Unique chunk content for testing ABC123" in full_content


def test_prompt_builder_graceful_on_missing_template():
    """PromptBuilder must not raise when template files are missing."""
    from ai.runtime.prompt_builder import PromptBuilder
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        # Empty directory — no template files at all
        builder = PromptBuilder(prompts_dir=Path(tmpdir))
        state = make_initial_state(
            inputs={"project_name": "GhostCo", "idea_brief": "Invisible product", "industry": "Stealth"},
        )
        # Must not raise
        messages, version = builder.build("missing_agent", state)

    assert isinstance(messages, list)
    assert len(messages) >= 1


def test_prompt_builder_repair_includes_errors():
    """PromptBuilder.build_repair() must include validation errors in the returned messages."""
    from ai.runtime.prompt_builder import PromptBuilder

    builder = PromptBuilder()
    state = make_initial_state(
        agent_id="idea_validator",
        inputs={"project_name": "TestCo", "idea_brief": "A plan", "industry": "Tech"},
    )
    original_output = '{"invalid": true}'
    errors = ["Field 'market_size' is required", "Field 'competitors' must be a list"]

    messages = builder.build_repair("idea_validator", state, original_output, errors)

    assert isinstance(messages, list)
    # All error messages should appear somewhere in the repair messages
    full_content = " ".join(m["content"] for m in messages)
    for error in errors:
        assert error in full_content, f"Error not found in repair messages: {error}"
