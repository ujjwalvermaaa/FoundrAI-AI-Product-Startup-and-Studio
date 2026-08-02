"""
ai.evaluation.fixtures.business_modeler_fixtures — Eval cases for business_modeler agent.

Module key: business_model
Schema: BusinessModelCanvas (all 9 canvas fields must be non-empty)
"""

from __future__ import annotations

from ai.evaluation.evaluator import EvalCase
from ai.schemas.business_model_canvas import VALID_FIXTURE

AGENT_ID = "business_modeler"
MODULE_KEY = "business_model"

# ── Happy path ─────────────────────────────────────────────────────────────────
# All 9 canvas blocks fully populated.
happy_path = EvalCase(
    case_name="happy_path",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "AI-powered startup studio."},
    expected_output=VALID_FIXTURE,
    should_pass=True,
)

# ── Edge case ──────────────────────────────────────────────────────────────────
# All 9 blocks present but with minimal single-word string values.
edge_case = EvalCase(
    case_name="edge_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "Minimal canvas."},
    expected_output={
        "value_proposition": "Speed",
        "customer_segments": "Founders",
        "channels": "Web",
        "customer_relationships": "Self-serve",
        "revenue_streams": "SaaS",
        "key_resources": "AI",
        "key_activities": "Development",
        "key_partnerships": "Cloud",
        "cost_structure": "Compute",
        "summary": "",
    },
    should_pass=True,
)

# ── Invalid case ───────────────────────────────────────────────────────────────
# One canvas block (cost_structure) is empty — schema model_validator should reject this.
invalid_case = EvalCase(
    case_name="invalid_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "Canvas with missing block."},
    expected_output={
        "value_proposition": "Speed",
        "customer_segments": "Founders",
        "channels": "Web",
        "customer_relationships": "Self-serve",
        "revenue_streams": "SaaS",
        "key_resources": "AI",
        "key_activities": "Development",
        "key_partnerships": "Cloud",
        "cost_structure": "",  # empty — should fail model_validator
        "summary": "",
    },
    should_pass=False,
)


def get_cases() -> list[EvalCase]:
    return [happy_path, edge_case, invalid_case]
