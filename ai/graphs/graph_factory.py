"""
GraphFactory — central registry for all FoundrAI LangGraph compiled graphs.

Lazy-loads and caches each compiled graph so they are compiled exactly once
at startup and reused on every invocation.

Usage::

    from ai.graphs.graph_factory import GraphFactory

    compiled = GraphFactory.get_graph("idea_validation")
    result = await compiled.ainvoke(state)

    agent_id = GraphFactory.get_agent_id("idea_validation")
    # → "idea_validator"
"""

from __future__ import annotations

import logging
from typing import Callable

from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph

logger = logging.getLogger(__name__)

# ── Module-to-agent-id mapping ───────────────────────────────────────────────

_AGENT_IDS: dict[str, str] = {
    "idea_validation": "idea_validator",
    "market_research": "market_researcher",
    "business_model": "business_modeler",
    "product_strategy": "product_strategist",
    "technical_architecture": "technical_architect",
    "financial_planning": "financial_analyst",
    "marketing_strategy": "marketing_strategist",
    "investor_documentation": "investor_writer",
}


# ── Lazy graph builder registry ───────────────────────────────────────────────

def _get_graph_builders() -> dict[str, Callable[[], StateGraph]]:
    """
    Return mapping of module_key → builder function.
    Imports are deferred here to avoid circular imports at module load time.
    """
    from ai.graphs.validation_graph import build_validation_graph
    from ai.graphs.market_research_graph import build_market_research_graph
    from ai.graphs.business_model_graph import build_business_model_graph
    from ai.graphs.product_strategy_graph import build_product_strategy_graph
    from ai.graphs.architecture_graph import build_architecture_graph
    from ai.graphs.financial_graph import build_financial_graph
    from ai.graphs.marketing_graph import build_marketing_graph
    from ai.graphs.investor_graph import build_investor_graph

    return {
        "idea_validation": build_validation_graph,
        "market_research": build_market_research_graph,
        "business_model": build_business_model_graph,
        "product_strategy": build_product_strategy_graph,
        "technical_architecture": build_architecture_graph,
        "financial_planning": build_financial_graph,
        "marketing_strategy": build_marketing_graph,
        "investor_documentation": build_investor_graph,
    }


class GraphFactory:
    """
    Central registry that maps module_key → compiled LangGraph graph.

    Graphs are compiled lazily on first access and cached for reuse.
    Thread-safe for read-after-write since assignment is atomic in CPython.
    """

    # Cache: module_key → CompiledGraph
    _cache: dict[str, CompiledGraph] = {}

    @classmethod
    def get_graph(cls, module_key: str) -> CompiledGraph:
        """
        Return the compiled graph for *module_key*.

        Compiles and caches on first call; returns cached instance thereafter.

        Args:
            module_key: One of the 8 FoundrAI module keys.

        Returns:
            A compiled LangGraph graph ready for ``ainvoke``.

        Raises:
            ValueError: If *module_key* is not recognised.
        """
        builders = _get_graph_builders()
        if module_key not in builders:
            raise ValueError(
                f"Unknown module_key: {module_key!r}. "
                f"Valid keys: {sorted(builders)}"
            )

        if module_key not in cls._cache:
            logger.info("GraphFactory: compiling graph for %r", module_key)
            cls._cache[module_key] = builders[module_key]().compile()
            logger.info("GraphFactory: graph for %r compiled and cached", module_key)

        return cls._cache[module_key]

    @classmethod
    def get_agent_id(cls, module_key: str) -> str:
        """
        Return the agent_id for *module_key*.

        Args:
            module_key: One of the 8 FoundrAI module keys.

        Returns:
            The agent identifier string (e.g. ``"idea_validator"``).

        Raises:
            ValueError: If *module_key* is not recognised.
        """
        if module_key not in _AGENT_IDS:
            raise ValueError(
                f"Unknown module_key: {module_key!r}. "
                f"Valid keys: {sorted(_AGENT_IDS)}"
            )
        return _AGENT_IDS[module_key]
