"""
ai.agents.marketing_strategist.agent — metadata constants for the Marketing Strategist agent.

These constants are referenced by the WorkflowService and the marketing graph
to identify the agent, its module, the artifact type it produces, and the
Pydantic schema used to validate its output.
"""

from __future__ import annotations

from ai.schemas.marketing_plan import MarketingPlan

AGENT_ID = "marketing_strategist"
MODULE_KEY = "marketing_strategy"
ARTIFACT_TYPE = "marketing_plan"
SCHEMA = MarketingPlan
