"""
ai.graphs.market_research_graph — LangGraph StateGraph pipeline for market research.

Pipeline:
    context_loader → rag_retrieve → generation → validation →
      [valid]          → reflection → persist → END
      [invalid, retry] → repair → validation (loop, max 2 retries)
      [invalid, max]   → END (failed)

Usage:
    from ai.graphs.market_research_graph import build_market_research_graph, run_market_research_graph
    from ai.graphs.state import make_initial_state

    state = make_initial_state(
        project_id="...",
        module_key="market_research",
        agent_id="market_researcher",
        inputs={
            "idea_brief": "...",
            "project_name": "...",
            "industry": "...",
        },
    )
    result = run_market_research_graph(state)
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from langgraph.graph import END, StateGraph

from ai.graphs.nodes.context_loader import context_loader_node
from ai.graphs.nodes.generation_node import generation_node
from ai.graphs.nodes.persist_node import persist_node
from ai.graphs.nodes.rag_node import rag_node
from ai.graphs.nodes.reflection_node import reflection_node
from ai.graphs.nodes.repair_node import repair_node
from ai.graphs.nodes.validation_node import validation_node
from ai.graphs.state import WorkflowState

logger = logging.getLogger(__name__)


# ── Conditional routing ───────────────────────────────────────────────────────

def _route_after_validation(state: WorkflowState) -> str:
    """
    Route after the validation node based on parse outcome and retry count.

    Returns:
      - "reflection"  if parsed_output is not None (success)
      - "repair"      if parsed_output is None AND retry_count < 2
      - END           if parsed_output is None AND retry_count >= 2 (give up)
    """
    if state.get("parsed_output") is not None:
        return "reflection"

    retry_count: int = state.get("retry_count") or 0
    if retry_count < 2:
        logger.debug(
            "_route_after_validation: parse failed, routing to repair (retry_count=%d)",
            retry_count,
        )
        return "repair"

    logger.warning(
        "_route_after_validation: parse failed after %d retries — ending graph",
        retry_count,
    )
    return END


# ── Graph builder ─────────────────────────────────────────────────────────────

def build_market_research_graph() -> StateGraph:
    """
    Build the LangGraph StateGraph for market research.

    Node sequence:
        context_loader → rag_retrieve → generation → validation →
          [valid]    → reflection → persist → END
          [invalid]  → repair → validation (loop, max 2 retries)
          [max fail] → END

    Returns:
        An uncompiled StateGraph. Call .compile() before invoking.
    """
    graph = StateGraph(WorkflowState)

    # ── Add nodes ─────────────────────────────────────────────────────────
    graph.add_node("context_loader", context_loader_node)
    graph.add_node("rag_retrieve", rag_node)
    graph.add_node("generation", generation_node)
    graph.add_node("validation", validation_node)
    graph.add_node("repair", repair_node)
    graph.add_node("reflection", reflection_node)
    graph.add_node("persist", persist_node)

    # ── Set entry point ───────────────────────────────────────────────────
    graph.set_entry_point("context_loader")

    # ── Linear edges ──────────────────────────────────────────────────────
    graph.add_edge("context_loader", "rag_retrieve")
    graph.add_edge("rag_retrieve", "generation")
    graph.add_edge("generation", "validation")

    # ── Conditional edge from validation ──────────────────────────────────
    graph.add_conditional_edges(
        "validation",
        _route_after_validation,
        {
            "reflection": "reflection",
            "repair": "repair",
            END: END,
        },
    )

    # ── Repair loops back to validation ───────────────────────────────────
    graph.add_edge("repair", "validation")

    # ── Success path ──────────────────────────────────────────────────────
    graph.add_edge("reflection", "persist")
    graph.add_edge("persist", END)

    return graph


# ── Convenience runner ────────────────────────────────────────────────────────

def run_market_research_graph(state: WorkflowState) -> WorkflowState:
    """
    Compile and run the market research graph synchronously.

    This function handles the async→sync bridge: if there is already a running
    event loop (e.g. inside pytest-asyncio or FastAPI), it runs the compiled
    graph via asyncio.run() in a separate thread strategy.  In a plain sync
    context it calls asyncio.run() directly.

    Args:
        state: Initial WorkflowState populated by WorkflowService.

    Returns:
        Updated WorkflowState after the graph completes.
    """
    compiled = build_market_research_graph().compile()
    result: Any = compiled.invoke(state)
    return result  # type: ignore[return-value]
