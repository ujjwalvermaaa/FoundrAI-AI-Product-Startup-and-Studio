"""
ai.agents.financial_analyst.agent — metadata constants for the Financial Analyst agent.

These constants are referenced by the WorkflowService and the financial graph
to identify the agent, its module, the artifact type it produces, and the
Pydantic schema used to validate its output.
"""

from __future__ import annotations

from ai.schemas.financial_model import FinancialModel

AGENT_ID = "financial_analyst"
MODULE_KEY = "financial_planning"
ARTIFACT_TYPE = "financial_model"
SCHEMA = FinancialModel
