"""
ai.evaluation.fixtures.product_strategist_fixtures — Eval cases for product_strategist agent.

Module key: product_strategy
Schema: ProductRoadmap (phases ≥ 2, each phase features ≥ 3)
"""

from __future__ import annotations

from ai.evaluation.evaluator import EvalCase
from ai.schemas.product_roadmap import VALID_FIXTURE

AGENT_ID = "product_strategist"
MODULE_KEY = "product_strategy"

# ── Happy path ─────────────────────────────────────────────────────────────────
# 2 phases, 3 features each — uses VALID_FIXTURE as base.
happy_path = EvalCase(
    case_name="happy_path",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "AI startup studio product."},
    expected_output=VALID_FIXTURE,
    should_pass=True,
)

# ── Edge case ──────────────────────────────────────────────────────────────────
# Exactly 2 phases with exactly 3 features per phase (minimum counts).
edge_case = EvalCase(
    case_name="edge_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "Minimal product roadmap."},
    expected_output={
        "phases": [
            {
                "name": "Phase 1",
                "description": "",
                "features": [
                    {"name": "Feature A", "description": "", "priority": "high"},
                    {"name": "Feature B", "description": "", "priority": "medium"},
                    {"name": "Feature C", "description": "", "priority": "low"},
                ],
                "timeline": "",
            },
            {
                "name": "Phase 2",
                "description": "",
                "features": [
                    {"name": "Feature D", "description": "", "priority": "high"},
                    {"name": "Feature E", "description": "", "priority": "medium"},
                    {"name": "Feature F", "description": "", "priority": "low"},
                ],
                "timeline": "",
            },
        ],
        "metrics": [],
        "assumptions": ["Assumption 1"],
        "summary": "",
    },
    should_pass=True,
)

# ── Invalid case ───────────────────────────────────────────────────────────────
# Only 1 phase — below the minimum of 2. Schema should reject this.
invalid_case = EvalCase(
    case_name="invalid_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "Single-phase roadmap — invalid."},
    expected_output={
        "phases": [
            {
                "name": "Phase 1",
                "description": "",
                "features": [
                    {"name": "Feature A", "description": "", "priority": "high"},
                    {"name": "Feature B", "description": "", "priority": "medium"},
                    {"name": "Feature C", "description": "", "priority": "low"},
                ],
                "timeline": "",
            },
        ],
        "metrics": [],
        "assumptions": [],
        "summary": "Only 1 phase — should fail.",
    },
    should_pass=False,
)


def get_cases() -> list[EvalCase]:
    return [happy_path, edge_case, invalid_case]
