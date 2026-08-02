"""
ai.agents.business_modeler.agent — metadata constants for the Business Modeler agent.

These constants are referenced by the WorkflowService and the business model graph
to identify the agent, its module, the artifact type it produces, and the
Pydantic schema used to validate its output.
"""

from __future__ import annotations

from ai.schemas.business_model_canvas import BusinessModelCanvas

AGENT_ID = "business_modeler"
MODULE_KEY = "business_model"
ARTIFACT_TYPE = "business_model_canvas"
SCHEMA = BusinessModelCanvas
