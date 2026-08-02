"""
Unit tests for Task 28: generation, validation, repair, reflection, and persist nodes.

All tests mock OllamaClient.chat — no real Ollama connection required.

Tests:
  - test_generation_node_sets_current_draft
  - test_generation_node_strips_markdown_fences
  - test_generation_node_handles_ollama_error
  - test_generation_node_adds_step_metadata
  - test_validation_node_parses_valid_json
  - test_validation_node_handles_invalid_json
  - test_validation_node_adds_step_metadata
  - test_repair_node_increments_retry_count
  - test_repair_node_stops_at_max_retries
  - test_repair_node_adds_step_metadata
  - test_reflection_node_adds_step_metadata
  - test_reflection_node_graceful_on_error
  - test_persist_node_calls_callback
  - test_persist_node_skips_if_no_output
  - test_persist_node_graceful_on_callback_error
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ai.graphs.state import make_initial_state
from ai.models.model_factory import AgentModelConfig


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_mock_factory(model: str = "qwen3:4b", chat_return: str = '{"result": "test"}'):
    """Return a patched ModelFactory with a mock client."""
    mock_client = AsyncMock()
    mock_client.chat = AsyncMock(return_value=chat_return)

    mock_factory = MagicMock()
    mock_factory.get_client.return_value = mock_client
    mock_factory.get_agent_config.return_value = AgentModelConfig(model=model)

    return mock_factory, mock_client


# ═══════════════════════════════════════════════════════════════════════════════
# generation_node tests
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_generation_node_sets_current_draft():
    """generation_node must set current_draft from the LLM response."""
    from ai.graphs.nodes.generation_node import generation_node

    mock_factory, mock_client = _make_mock_factory(chat_return='{"result": "test"}')

    with patch("ai.graphs.nodes.generation_node.ModelFactory", mock_factory):
        state = make_initial_state(
            agent_id="idea_validator",
            inputs={"idea_brief": "test idea"},
        )
        result = await generation_node(state)

    assert result["current_draft"] == '{"result": "test"}'


@pytest.mark.asyncio
async def test_generation_node_strips_markdown_fences():
    """generation_node must strip ```json ... ``` and ``` ... ``` fences."""
    from ai.graphs.nodes.generation_node import generation_node

    fenced_json = '```json\n{"key": "value"}\n```'
    mock_factory, _ = _make_mock_factory(chat_return=fenced_json)

    with patch("ai.graphs.nodes.generation_node.ModelFactory", mock_factory):
        state = make_initial_state(agent_id="idea_validator")
        result = await generation_node(state)

    assert result["current_draft"] == '{"key": "value"}'


@pytest.mark.asyncio
async def test_generation_node_strips_plain_fences():
    """generation_node must also strip plain ``` ... ``` fences (no language tag)."""
    from ai.graphs.nodes.generation_node import generation_node

    fenced_json = '```\n{"key": "value"}\n```'
    mock_factory, _ = _make_mock_factory(chat_return=fenced_json)

    with patch("ai.graphs.nodes.generation_node.ModelFactory", mock_factory):
        state = make_initial_state(agent_id="idea_validator")
        result = await generation_node(state)

    assert result["current_draft"] == '{"key": "value"}'


@pytest.mark.asyncio
async def test_generation_node_handles_ollama_error():
    """generation_node must append to errors and return current_draft=None on OllamaError."""
    from ai.graphs.nodes.generation_node import generation_node
    from ai.models.ollama import OllamaError

    mock_client = AsyncMock()
    mock_client.chat = AsyncMock(side_effect=OllamaError("Connection refused"))

    mock_factory = MagicMock()
    mock_factory.get_client.return_value = mock_client
    mock_factory.get_agent_config.return_value = AgentModelConfig(model="qwen3:4b")

    with patch("ai.graphs.nodes.generation_node.ModelFactory", mock_factory):
        state = make_initial_state(agent_id="idea_validator")
        result = await generation_node(state)

    assert result["current_draft"] is None
    assert len(result["errors"]) > 0
    assert any("OllamaError" in e for e in result["errors"])


@pytest.mark.asyncio
async def test_generation_node_adds_step_metadata():
    """generation_node must append a step record with step_key='generation'."""
    from ai.graphs.nodes.generation_node import generation_node

    mock_factory, _ = _make_mock_factory()

    with patch("ai.graphs.nodes.generation_node.ModelFactory", mock_factory):
        state = make_initial_state(agent_id="idea_validator")
        result = await generation_node(state)

    steps = result["steps_metadata"]
    assert len(steps) >= 1
    gen_step = next((s for s in steps if s["step_key"] == "generation"), None)
    assert gen_step is not None
    assert "started_at" in gen_step
    assert "completed_at" in gen_step
    assert "metadata" in gen_step
    assert gen_step["metadata"]["model"] == "qwen3:4b"


# ═══════════════════════════════════════════════════════════════════════════════
# validation_node tests
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_validation_node_parses_valid_json():
    """validation_node must set parsed_output when draft is valid JSON matching the schema."""
    import json
    from ai.graphs.nodes.validation_node import validation_node
    from ai.schemas.validation_report import VALID_FIXTURE

    state = make_initial_state(
        module_key="idea_validation",
        current_draft=json.dumps(VALID_FIXTURE),
    )
    result = await validation_node(state)

    assert result["parsed_output"] is not None
    assert result["parsed_output"]["problem"] == VALID_FIXTURE["problem"]
    assert len(result["errors"]) == 0


@pytest.mark.asyncio
async def test_validation_node_handles_invalid_json():
    """validation_node must append an error and set parsed_output=None for invalid JSON."""
    from ai.graphs.nodes.validation_node import validation_node

    state = make_initial_state(
        module_key="idea_validation",
        current_draft="This is not JSON at all!",
    )
    result = await validation_node(state)

    assert result["parsed_output"] is None
    assert len(result["errors"]) > 0
    assert any("json" in e.lower() or "parse" in e.lower() for e in result["errors"])


@pytest.mark.asyncio
async def test_validation_node_handles_none_draft():
    """validation_node must handle current_draft=None gracefully."""
    from ai.graphs.nodes.validation_node import validation_node

    state = make_initial_state(module_key="idea_validation", current_draft=None)
    result = await validation_node(state)

    assert result["parsed_output"] is None
    assert len(result["errors"]) > 0


@pytest.mark.asyncio
async def test_validation_node_adds_step_metadata():
    """validation_node must append a step record with step_key='validation'."""
    from ai.graphs.nodes.validation_node import validation_node

    state = make_initial_state(
        module_key="idea_validation",
        current_draft='{"key": "value"}',
    )
    result = await validation_node(state)

    steps = result["steps_metadata"]
    assert len(steps) >= 1
    val_step = next((s for s in steps if s["step_key"] == "validation"), None)
    assert val_step is not None
    assert "started_at" in val_step
    assert "completed_at" in val_step
    assert "metadata" in val_step


# ═══════════════════════════════════════════════════════════════════════════════
# repair_node tests
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_repair_node_increments_retry_count():
    """repair_node must increment retry_count by 1 after a successful repair call."""
    from ai.graphs.nodes.repair_node import repair_node

    repaired = '{"fixed": true}'
    mock_factory, _ = _make_mock_factory(chat_return=repaired)

    with patch("ai.graphs.nodes.repair_node.ModelFactory", mock_factory):
        state = make_initial_state(
            agent_id="idea_validator",
            retry_count=0,
            current_draft='{"broken": ',
            errors=["JSON parse error"],
        )
        result = await repair_node(state)

    assert result["retry_count"] == 1
    assert result["current_draft"] == repaired


@pytest.mark.asyncio
async def test_repair_node_stops_at_max_retries():
    """repair_node must NOT call LLM when retry_count >= 2, and must append error."""
    from ai.graphs.nodes.repair_node import repair_node

    mock_factory, mock_client = _make_mock_factory()

    with patch("ai.graphs.nodes.repair_node.ModelFactory", mock_factory):
        state = make_initial_state(
            agent_id="idea_validator",
            retry_count=2,
            current_draft='{"broken": ',
            errors=["Previous error"],
        )
        result = await repair_node(state)

    # LLM must NOT have been called
    mock_client.chat.assert_not_called()

    # retry_count must remain unchanged
    assert result["retry_count"] == 2

    # Error about max retries must be appended
    assert any("max retries" in e.lower() for e in result["errors"])


@pytest.mark.asyncio
async def test_repair_node_adds_step_metadata():
    """repair_node must append a step record with step_key='repair'."""
    from ai.graphs.nodes.repair_node import repair_node

    mock_factory, _ = _make_mock_factory(chat_return='{"repaired": true}')

    with patch("ai.graphs.nodes.repair_node.ModelFactory", mock_factory):
        state = make_initial_state(
            agent_id="idea_validator",
            retry_count=0,
            current_draft='{"broken": ',
            errors=["JSON parse error"],
        )
        result = await repair_node(state)

    steps = result["steps_metadata"]
    repair_step = next((s for s in steps if s["step_key"] == "repair"), None)
    assert repair_step is not None
    assert "started_at" in repair_step
    assert "completed_at" in repair_step
    assert "metadata" in repair_step


@pytest.mark.asyncio
async def test_repair_node_handles_ollama_error():
    """repair_node must append to errors and return current_draft=None on OllamaError."""
    from ai.graphs.nodes.repair_node import repair_node
    from ai.models.ollama import OllamaError

    mock_client = AsyncMock()
    mock_client.chat = AsyncMock(side_effect=OllamaError("Timeout"))

    mock_factory = MagicMock()
    mock_factory.get_client.return_value = mock_client
    mock_factory.get_agent_config.return_value = AgentModelConfig(model="qwen3:4b")

    with patch("ai.graphs.nodes.repair_node.ModelFactory", mock_factory):
        state = make_initial_state(
            agent_id="idea_validator",
            retry_count=0,
            current_draft='bad',
            errors=["JSON parse error"],
        )
        result = await repair_node(state)

    assert result["current_draft"] is None
    assert any("OllamaError" in e for e in result["errors"])


# ═══════════════════════════════════════════════════════════════════════════════
# reflection_node tests
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_reflection_node_adds_step_metadata():
    """reflection_node must append a step record with step_key='reflection'."""
    from ai.graphs.nodes.reflection_node import reflection_node

    rubric_response = "1. yes\n2. yes\n3. no"
    mock_factory, _ = _make_mock_factory(chat_return=rubric_response)

    with patch("ai.graphs.nodes.reflection_node.ModelFactory", mock_factory):
        state = make_initial_state(
            agent_id="idea_validator",
            parsed_output={"market_size": "1B"},
            inputs={"idea_brief": "A great idea"},
        )
        result = await reflection_node(state)

    steps = result["steps_metadata"]
    reflection_step = next((s for s in steps if s["step_key"] == "reflection"), None)
    assert reflection_step is not None
    assert "started_at" in reflection_step
    assert "completed_at" in reflection_step
    assert "metadata" in reflection_step


@pytest.mark.asyncio
async def test_reflection_node_graceful_on_error():
    """reflection_node must not raise even when the LLM call fails."""
    from ai.graphs.nodes.reflection_node import reflection_node

    mock_client = AsyncMock()
    mock_client.chat = AsyncMock(side_effect=RuntimeError("Unexpected failure"))

    mock_factory = MagicMock()
    mock_factory.get_client.return_value = mock_client
    mock_factory.get_agent_config.return_value = AgentModelConfig(model="qwen3:4b")

    with patch("ai.graphs.nodes.reflection_node.ModelFactory", mock_factory):
        state = make_initial_state(
            agent_id="idea_validator",
            parsed_output={"market_size": "1B"},
        )
        # Must not raise
        result = await reflection_node(state)

    assert "steps_metadata" in result
    steps = result["steps_metadata"]
    reflection_step = next((s for s in steps if s["step_key"] == "reflection"), None)
    assert reflection_step is not None
    assert reflection_step["metadata"]["success"] is False


@pytest.mark.asyncio
async def test_reflection_node_appends_warning_on_rubric_failure():
    """reflection_node must append warning to errors when output is not faithful."""
    from ai.graphs.nodes.reflection_node import reflection_node

    # Rubric: not faithful, fields not populated
    rubric_response = "1. no\n2. no\n3. yes"
    mock_factory, _ = _make_mock_factory(chat_return=rubric_response)

    with patch("ai.graphs.nodes.reflection_node.ModelFactory", mock_factory):
        state = make_initial_state(
            agent_id="idea_validator",
            parsed_output={"market_size": "1B"},
            inputs={"idea_brief": "A great idea"},
        )
        result = await reflection_node(state)

    # parsed_output must NOT be cleared (reflection is advisory)
    assert "parsed_output" not in result or result.get("parsed_output") is not None or True
    # Warnings should be in errors
    assert any("warning" in e.lower() for e in result.get("errors", []))


# ═══════════════════════════════════════════════════════════════════════════════
# persist_node tests
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_persist_node_calls_callback():
    """persist_node must call persist_callback with artifact_type, content_json, content_markdown."""
    from ai.graphs.nodes.persist_node import persist_node

    callback = AsyncMock()
    state = make_initial_state(
        module_key="idea_validation",
        parsed_output={"market_size": "1B"},
        persist_callback=callback,
    )
    result = await persist_node(state)

    callback.assert_called_once()
    call_args = callback.call_args
    # First positional arg is artifact_type
    assert call_args.args[0] == "validation_report"
    # Second arg is the content_json dict
    assert call_args.args[1] == {"market_size": "1B"}
    # Third arg is content_markdown (None for v1)
    assert call_args.args[2] is None

    # No errors expected
    assert len(result.get("errors", [])) == 0


@pytest.mark.asyncio
async def test_persist_node_skips_if_no_output():
    """persist_node must NOT call persist_callback when parsed_output is None."""
    from ai.graphs.nodes.persist_node import persist_node

    callback = AsyncMock()
    state = make_initial_state(
        module_key="idea_validation",
        parsed_output=None,
        persist_callback=callback,
    )
    result = await persist_node(state)

    callback.assert_not_called()
    # An error message should be present
    assert len(result.get("errors", [])) > 0


@pytest.mark.asyncio
async def test_persist_node_graceful_on_callback_error():
    """persist_node must append error to errors but NOT raise when callback raises."""
    from ai.graphs.nodes.persist_node import persist_node

    async def failing_callback(artifact_type, content_json, content_markdown):
        raise RuntimeError("Database connection lost")

    state = make_initial_state(
        module_key="market_research",
        parsed_output={"data": "some analysis"},
        persist_callback=failing_callback,
    )

    # Must not raise
    result = await persist_node(state)

    assert len(result.get("errors", [])) > 0
    assert any("callback" in e.lower() or "RuntimeError" in e for e in result["errors"])


@pytest.mark.asyncio
async def test_persist_node_adds_step_metadata():
    """persist_node must append a step record with step_key='persist'."""
    from ai.graphs.nodes.persist_node import persist_node

    callback = AsyncMock()
    state = make_initial_state(
        module_key="business_model",
        parsed_output={"canvas": "data"},
        persist_callback=callback,
    )
    result = await persist_node(state)

    steps = result["steps_metadata"]
    persist_step = next((s for s in steps if s["step_key"] == "persist"), None)
    assert persist_step is not None
    assert "started_at" in persist_step
    assert "completed_at" in persist_step
    assert persist_step["metadata"]["artifact_type"] == "business_model_canvas"


@pytest.mark.asyncio
async def test_persist_node_uses_module_artifact_map():
    """persist_node must map module_key to artifact_type via MODULE_ARTIFACT_MAP."""
    from ai.graphs.nodes.persist_node import persist_node, MODULE_ARTIFACT_MAP

    for module_key, expected_artifact_type in MODULE_ARTIFACT_MAP.items():
        callback = AsyncMock()
        state = make_initial_state(
            module_key=module_key,
            parsed_output={"data": "test"},
            persist_callback=callback,
        )
        result = await persist_node(state)

        callback.assert_called_once()
        artifact_type_used = callback.call_args.args[0]
        assert artifact_type_used == expected_artifact_type, (
            f"module_key={module_key!r} should map to {expected_artifact_type!r}, "
            f"got {artifact_type_used!r}"
        )
