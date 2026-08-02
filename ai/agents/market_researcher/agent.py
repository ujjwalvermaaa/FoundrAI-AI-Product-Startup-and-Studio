"""
ai.agents.market_researcher.agent — metadata constants for the Market Researcher agent.

These constants are referenced by the WorkflowService and the market research graph
to identify the agent, its module, the artifact type it produces, and the
Pydantic schema used to validate its output.
"""

from __future__ import annotations

from ai.schemas.market_analysis import MarketAnalysis

AGENT_ID = "market_researcher"
MODULE_KEY = "market_research"
ARTIFACT_TYPE = "market_analysis"
SCHEMA = MarketAnalysis
