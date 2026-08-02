"""
ai.evaluation.fixtures.marketing_strategist_fixtures — Eval cases for marketing_strategist agent.

Module key: marketing_strategy
Schema: MarketingPlan (channels ≥ 3, launch_checklist ≥ 5)
"""

from __future__ import annotations

from ai.evaluation.evaluator import EvalCase
from ai.schemas.marketing_plan import VALID_FIXTURE

AGENT_ID = "marketing_strategist"
MODULE_KEY = "marketing_strategy"

# ── Happy path ─────────────────────────────────────────────────────────────────
# 4 channels, 6 launch checklist items — uses VALID_FIXTURE as base.
happy_path = EvalCase(
    case_name="happy_path",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "AI startup marketing strategy."},
    expected_output=VALID_FIXTURE,
    should_pass=True,
)

# ── Edge case ──────────────────────────────────────────────────────────────────
# Exactly 3 channels (minimum) and exactly 5 checklist items (minimum).
edge_case = EvalCase(
    case_name="edge_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "Minimal marketing plan."},
    expected_output={
        "icp": "Early-stage founders",
        "messaging": "Validate fast with AI.",
        "channels": [
            "Product Hunt",
            "LinkedIn",
            "Twitter/X",
        ],
        "launch_checklist": [
            "Set up landing page",
            "Record demo video",
            "Reach out to 20 beta users",
            "Prepare Product Hunt assets",
            "Schedule launch posts",
        ],
        "calendar": {},
        "summary": "",
    },
    should_pass=True,
)

# ── Invalid case ───────────────────────────────────────────────────────────────
# Only 2 channels — below the minimum of 3. Schema should reject this.
invalid_case = EvalCase(
    case_name="invalid_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "Marketing plan with too few channels."},
    expected_output={
        "icp": "Founders",
        "messaging": "Build fast.",
        "channels": [
            "Product Hunt",
            "LinkedIn",
            # Only 2 channels — should fail
        ],
        "launch_checklist": [
            "Set up landing page",
            "Record demo",
            "Beta outreach",
            "Prepare assets",
            "Launch posts",
        ],
        "calendar": {},
        "summary": "Only 2 channels — should fail.",
    },
    should_pass=False,
)


def get_cases() -> list[EvalCase]:
    return [happy_path, edge_case, invalid_case]
