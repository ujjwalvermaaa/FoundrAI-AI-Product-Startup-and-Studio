"""
ai.agents.technical_architect.agent — metadata constants for the Technical Architect agent.

These constants are referenced by the WorkflowService and the architecture graph
to identify the agent, its module, the artifact type it produces, and the
Pydantic schema used to validate its output.
"""

from __future__ import annotations

from ai.schemas.architecture_doc import ArchitectureDoc

AGENT_ID = "technical_architect"
MODULE_KEY = "technical_architecture"
ARTIFACT_TYPE = "architecture_doc"
SCHEMA = ArchitectureDoc
