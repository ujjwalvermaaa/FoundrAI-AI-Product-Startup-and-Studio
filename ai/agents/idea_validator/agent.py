"""
ai.agents.idea_validator.agent — metadata constants for the Idea Validator agent.

These constants are referenced by the WorkflowService and the validation graph
to identify the agent, its module, the artifact type it produces, and the
Pydantic schema used to validate its output.
"""

from __future__ import annotations

from ai.schemas.validation_report import ValidationReport

AGENT_ID = "idea_validator"
MODULE_KEY = "idea_validation"
ARTIFACT_TYPE = "validation_report"
SCHEMA = ValidationReport
