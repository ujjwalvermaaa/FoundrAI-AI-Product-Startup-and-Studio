"""
Unit tests for Task 35: Financial Analyst Agent and Financial Graph.

Tests:
  - test_financial_graph_compiles
  - test_financial_graph_nodes
  - test_financial_analyst_agent_constants
  - test_financial_analyst_prompt_files_exist
  - test_financial_graph_runs_with_mock_llm
  - test_financial_graph_triggers_repair_on_bad_json
  - test_financial_graph_fails_gracefully
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai.graphs.state import make_initial_state
from ai.models.model_factory import AgentModelConfig
from ai.schemas.financial_model import VALID_FIXTURE


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_mock_factory(chat_return: str = ""):
    mock_client = AsyncMock()
    mock_client.chat = AsyncMock(return_value=chat_return)
    mock_factory = MagicMock()
    mock_factory.get_client.return_value = mock_client
    mock_factory.get_agent_config.return_value = AgentModelConfig(model="qwen3:4b")
    return mock_factory, mock_client


def _make_state(**kwargs):
    return make_initial_state(
        project_id="test-project",
        module_key="financial_planning",
        agent_id="financial_analyst",
        inputs={
            "idea_brief": "AI startup for founders",
            "project_name": "FoundrAI",
            "industry": "Technology",
        },
        required_artifacts={
            "business_model_canvas": {
                "value_proposition": "AI-powered startup validation in minutes.",
                "revenue_streams": ["SaaS subscriptions", "Pay-per-report"],
            },
            "product_roadmap": {
                "phases": [
                    {"name": "MVP", "features": ["auth", "validation"], "timeline": "Q1 2025"},
                ],
                "summary": "Two-phase roadmap.",
            },
        },
        **kwargs,
    )


# ── Test 1: graph compiles ────────────────────────────────────────────────────

def test_financial_graph_compiles():
    """build_financial_graph() must return a StateGraph without raising."""
    from ai.graphs.financial_graph import build_financial_graph
    from langgraph.graph import StateGraph

    graph = build_financial_graph()
    assert graph is not None
    assert isinstance(graph, StateGraph)

    compiled = graph.compile()
    assert compiled is not None


# ── Test 2: graph has all 7 nodes ─────────────────────────────────────────────

def test_financial_graph_nodes():
    """Compiled graph must have all 7 expected nodes."""
    from ai.graphs.financial_graph import build_financial_graph

    compiled = build_financial_graph().compile()
    graph_repr = compiled.get_graph()
    node_ids = set(graph_repr.nodes.keys())

    expected_nodes = {
        "context_loader", "rag_retrieve", "generation",
        "validation", "repair", "reflection", "persist",
    }
    for node in expected_nodes:
        assert node in node_ids, f"Missing node in compiled graph: {node!r}"


# ── Test 3: agent constants ───────────────────────────────────────────────────

def test_financial_analyst_agent_constants():
    """AGENT_ID, MODULE_KEY, ARTIFACT_TYPE, and SCHEMA must be correct."""
    from ai.agents.financial_analyst.agent import AGENT_ID, MODULE_KEY, ARTIFACT_TYPE, SCHEMA
    from ai.schemas.financial_model import FinancialModel

    assert AGENT_ID == "financial_analyst"
    assert MODULE_KEY == "financial_planning"
    assert ARTIFACT_TYPE == "financial_model"
    assert SCHEMA is FinancialModel


# ── Test 4: prompt files exist ────────────────────────────────────────────────

def test_financial_analyst_prompt_files_exist():
    """All 4 prompt template files must exist on disk with non-empty content."""
    prompts_dir = (
        Path(__file__).parent.parent.parent.parent
        / "ai" / "prompts" / "agents" / "financial_analyst"
    )

    for filename in ["system.v1.md", "developer.v1.md", "user.v1.md", "repair.v1.md"]:
        filepath = prompts_dir / filename
        assert filepath.exists(), f"Missing prompt file: {filepath}"
        assert len(filepath.read_text(encoding="utf-8").strip()) > 0, f"Empty: {filepath}"


# ── Test 5: graph runs end-to-end with valid mock LLM ─────────────────────────

@pytest.mark.asyncio
async def test_financial_graph_runs_with_mock_llm():
    """Run graph end-to-end with a mocked LLM returning valid JSON."""
    from ai.graphs.financial_graph import build_financial_graph

    valid_json = json.dumps(VALID_FIXTURE)
    mock_factory, _ = _make_mock_factory(chat_return=valid_json)

    with (
        patch("ai.graphs.nodes.generation_node.ModelFactory", mock_factory),
        patch("ai.graphs.nodes.repair_node.ModelFactory", mock_factory),
        patch("ai.graphs.nodes.reflection_node.ModelFactory", mock_factory),
        patch("ai.graphs.nodes.rag_node._search_safe", return_value=[]),
    ):
        state = _make_state()
        compiled = build_financial_graph().compile()
        result = await compiled.ainvoke(state)

    assert result.get("parsed_output") is not None, (
        f"parsed_output should be set; errors={result.get('errors')}"
    )
    assert len(result["parsed_output"]["assumptions"]) >= 5


# ── Test 6: graph triggers repair on bad JSON ─────────────────────────────────

@pytest.mark.asyncio
async def test_financial_graph_triggers_repair_on_bad_json():
    """Run graph with mock LLM returning bad JSON first, then valid JSON."""
    from ai.graphs.financial_graph import build_financial_graph

    valid_json = json.dumps(VALID_FIXTURE)
    call_count = {"n": 0}

    async def _side_effect(*args, **kwargs):
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
        compiled = build_financial_graph().compile()
        result = await compiled.ainvoke(state)

    assert call_count["n"] > 1, "Expected LLM to be called more than once (repair triggered)"
    assert (result.get("retry_count") or 0) > 0, "retry_count should be > 0 after repair"
    assert result.get("parsed_output") is not None, (
        f"parsed_output should be set after repair; errors={result.get('errors')}"
    )


# ── Test 7: graph fails gracefully on persistent invalid JSON ─────────────────

@pytest.mark.asyncio
async def test_financial_graph_fails_gracefully():
    """Run graph with mock LLM always returning invalid JSON."""
    from ai.graphs.financial_graph import build_financial_graph

    mock_factory, _ = _make_mock_factory(chat_return="ALWAYS BROKEN JSON <<<")

    with (
        patch("ai.graphs.nodes.generation_node.ModelFactory", mock_factory),
        patch("ai.graphs.nodes.repair_node.ModelFactory", mock_factory),
        patch("ai.graphs.nodes.reflection_node.ModelFactory", mock_factory),
        patch("ai.graphs.nodes.rag_node._search_safe", return_value=[]),
    ):
        state = _make_state()
        compiled = build_financial_graph().compile()
        result = await compiled.ainvoke(state)

    assert len(result.get("errors", [])) > 0, "errors list should be non-empty after exhausting retries"
    assert result.get("parsed_output") is None, "parsed_output should be None when all attempts fail"
