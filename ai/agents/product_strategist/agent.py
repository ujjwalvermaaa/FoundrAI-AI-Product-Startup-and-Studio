"""
ai.agents.product_strategist.agent — metadata constants for the Product Strategist agent.

These constants are referenced by the WorkflowService and the product strategy graph
to identify the agent, its module, the artifact type it produces, and the
Pydantic schema used to validate its output.
"""

from __future__ import annotations

from ai.schemas.product_roadmap import ProductRoadmap

AGENT_ID = "product_strategist"
MODULE_KEY = "product_strategy"
ARTIFACT_TYPE = "product_roadmap"
SCHEMA = ProductRoadmap
