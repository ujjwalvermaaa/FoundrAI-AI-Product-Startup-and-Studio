"""
Unit tests for Task 31: Market Researcher Agent and Market Research Graph.

Tests:
  - test_market_research_graph_compiles
  - test_market_research_graph_nodes
  - test_market_researcher_agent_constants
  - test_market_researcher_prompt_files_exist
  - test_market_research_graph_runs_with_mock_llm
  - test_market_research_graph_triggers_repair_on_bad_json
  - test_market_research_graph_fails_gracefully
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai.graphs.state import make_initial_state
from ai.models.model_factory import AgentModelConfig
from ai.schemas.market_analysis import VALID_FIXTURE


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_mock_factory(chat_return: str = ""):
    """Return a MagicMock ModelFactory that yields an async client with a fixed chat response."""
    mock_client = AsyncMock()
    mock_client.chat = AsyncMock(return_value=chat_return)

    mock_factory = MagicMock()
    mock_factory.get_client.return_value = mock_client
    mock_factory.get_agent_config.return_value = AgentModelConfig(model="qwen3:4b")

    return mock_factory, mock_client


def _make_state(**kwargs):
    """Convenience: make a WorkflowState with market_researcher defaults."""
    return make_initial_state(
        project_id="test-project",
        module_key="market_research",
        agent_id="market_researcher",
        inputs={
            "idea_brief": "AI startup for founders",
            "project_name": "FoundrAI",
            "industry": "Technology",
        },
        required_artifacts={
            "validation_report": {
                "problem": "Founders lack structured tools for startup validation",
                "solution": "AI-powered validation platform",
                "validation_score": 78,
                "summary": "Strong opportunity in underserved founder tooling market.",
            }
        },
        **kwargs,
    )


# ── Test 1: graph compiles ────────────────────────────────────────────────────

def test_market_research_graph_compiles():
    """build_market_research_graph() must return a StateGraph without raising."""
    from ai.graphs.market_research_graph import build_market_research_graph
    from langgraph.graph import StateGraph

    graph = build_market_research_graph()
    assert graph is not None
    assert isinstance(graph, StateGraph)

    # Also ensure it compiles cleanly
    compiled = graph.compile()
    assert compiled is not None


# ── Test 2: graph has all 7 nodes ─────────────────────────────────────────────

def test_market_research_graph_nodes():
    """Compiled graph must have all 7 expected nodes."""
    from ai.graphs.market_research_graph import build_market_research_graph

    compiled = build_market_research_graph().compile()

    graph_repr = compiled.get_graph()
    node_ids = set(graph_repr.nodes.keys())

    expected_nodes = {
        "context_loader",
        "rag_retrieve",
        "generation",
        "validation",
        "repair",
        "reflection",
        "persist",
    }
    for node in expected_nodes:
        assert node in node_ids, f"Missing node in compiled graph: {node!r}"


# ── Test 3: agent constants ───────────────────────────────────────────────────

def test_market_researcher_agent_constants():
    """AGENT_ID, MODULE_KEY, ARTIFACT_TYPE, and SCHEMA must be correct."""
    from ai.agents.market_researcher.agent import AGENT_ID, MODULE_KEY, ARTIFACT_TYPE, SCHEMA
    from ai.schemas.market_analysis import MarketAnalysis

    assert AGENT_ID == "market_researcher"
    assert MODULE_KEY == "market_research"
    assert ARTIFACT_TYPE == "market_analysis"
    assert SCHEMA is MarketAnalysis


# ── Test 4: prompt files exist ────────────────────────────────────────────────

def test_market_researcher_prompt_files_exist():
    """All 4 prompt template files must exist on disk with non-empty content."""
    prompts_dir = (
        Path(__file__).parent.parent.parent.parent  # repo root
        / "ai" / "prompts" / "agents" / "market_researcher"
    )

    expected_files = [
        "system.v1.md",
        "developer.v1.md",
        "user.v1.md",
        "repair.v1.md",
    ]

    for filename in expected_files:
        filepath = prompts_dir / filename
        assert filepath.exists(), f"Missing prompt file: {filepath}"
        content = filepath.read_text(encoding="utf-8").strip()
        assert len(content) > 0, f"Prompt file is empty: {filepath}"


# ── Test 5: graph runs end-to-end with valid mock LLM ─────────────────────────

@pytest.mark.asyncio
async def test_market_research_graph_runs_with_mock_llm():
    """
    Run graph end-to-end with a mocked LLM returning valid JSON.
    Verify that parsed_output is populated in the result.
    """
    from ai.graphs.market_research_graph import build_market_research_graph

    valid_json = json.dumps(VALID_FIXTURE)
    mock_factory, _ = _make_mock_factory(chat_return=valid_json)

    with (
        patch("ai.graphs.nodes.generation_node.ModelFactory", mock_factory),
        patch("ai.graphs.nodes.repair_node.ModelFactory", mock_factory),
        patch("ai.graphs.nodes.reflection_node.ModelFactory", mock_factory),
        patch("ai.graphs.nodes.rag_node._search_safe", return_value=[]),
    ):
        state = _make_state()
        compiled = build_market_research_graph().compile()
        result = await compiled.ainvoke(state)

    assert result.get("parsed_output") is not None, (
        f"parsed_output should be set; errors={result.get('errors')}"
    )
    assert result["parsed_output"]["summary"] == VALID_FIXTURE["summary"]
    assert len(result["parsed_output"]["competitors"]) >= 3


# ── Test 6: graph triggers repair on bad JSON ─────────────────────────────────

@pytest.mark.asyncio
async def test_market_research_graph_triggers_repair_on_bad_json():
    """
    Run graph with mock LLM returning bad JSON first, then valid JSON.
    Verify that repair was triggered (retry_count > 0 in result).
    """
    from ai.graphs.market_research_graph import build_market_research_graph

    valid_json = json.dumps(VALID_FIXTURE)
    call_count = {"n": 0}

    async def _side_effect(*args, **kwargs):
        """First call returns broken JSON; subsequent calls return valid JSON."""
        call_count["n"] += 1
        if call_count["n"] == 1:
            return "NOT VALID JSON !!!"
        return valid_json

    mock_client = AsyncMock()
    mock_client.chat = AsyncMock(side_effect=_side_effect)

    mock_factory = MagicMock()
    mock_factory.get_client.return_value = mock_client
    mock_factory.get_agent_config.return_value = AgentModelConfig(model="qwen3:4b")

    with (
        patch("ai.graphs.nodes.generation_node.ModelFactory", mock_factory),
        patch("ai.graphs.nodes.repair_node.ModelFactory", mock_factory),
        patch("ai.graphs.nodes.reflection_node.ModelFactory", mock_factory),
        patch("ai.graphs.nodes.rag_node._search_safe", return_value=[]),
    ):
        state = _make_state()
        compiled = build_market_research_graph().compile()
        result = await compiled.ainvoke(state)

    # LLM was called more than once — repair was triggered
    assert call_count["n"] > 1, "Expected LLM to be called more than once (repair triggered)"
    # retry_count should be > 0 since repair ran
    assert (result.get("retry_count") or 0) > 0, (
        "retry_count should be > 0 after repair was triggered"
    )
    # Despite the initial bad response, the second call succeeded
    assert result.get("parsed_output") is not None, (
        f"parsed_output should be set after successful repair; errors={result.get('errors')}"
    )


# ── Test 7: graph fails gracefully on persistent invalid JSON ─────────────────

@pytest.mark.asyncio
async def test_market_research_graph_fails_gracefully():
    """
    Run graph with mock LLM always returning invalid JSON.
    Verify that errors list is non-empty and graph completes without raising.
    """
    from ai.graphs.market_research_graph import build_market_research_graph

    mock_factory, _ = _make_mock_factory(chat_return="ALWAYS BROKEN JSON <<<")

    with (
        patch("ai.graphs.nodes.generation_node.ModelFactory", mock_factory),
        patch("ai.graphs.nodes.repair_node.ModelFactory", mock_factory),
        patch("ai.graphs.nodes.reflection_node.ModelFactory", mock_factory),
        patch("ai.graphs.nodes.rag_node._search_safe", return_value=[]),
    ):
        state = _make_state()
        compiled = build_market_research_graph().compile()

        # Must NOT raise — graph handles failures gracefully
        result = await compiled.ainvoke(state)

    # After exhausting retries, errors must be populated
    assert len(result.get("errors", [])) > 0, (
        "errors list should be non-empty when graph exhausts retries"
    )
    # parsed_output remains None
    assert result.get("parsed_output") is None, (
        "parsed_output should be None when all attempts fail"
    )
