"""
ai.agents.investor_writer.agent — metadata constants for the Investor Writer agent.

These constants are referenced by the WorkflowService and the investor graph
to identify the agent, its module, the artifact type it produces, and the
Pydantic schema used to validate its output.
"""

from __future__ import annotations

from ai.schemas.investor_deck_outline import InvestorDeckOutline

AGENT_ID = "investor_writer"
MODULE_KEY = "investor_documentation"
ARTIFACT_TYPE = "investor_deck_outline"
SCHEMA = InvestorDeckOutline
