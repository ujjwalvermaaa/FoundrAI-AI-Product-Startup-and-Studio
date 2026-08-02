"""
ai.evaluation.fixtures.financial_analyst_fixtures — Eval cases for financial_analyst agent.

Module key: financial_planning
Schema: FinancialModel (assumptions ≥ 5, projection_12_months with 12 entries)
"""

from __future__ import annotations

from ai.evaluation.evaluator import EvalCase
from ai.schemas.financial_model import VALID_FIXTURE

AGENT_ID = "financial_analyst"
MODULE_KEY = "financial_planning"

# ── Happy path ─────────────────────────────────────────────────────────────────
# 12-month projection, 5 assumptions — uses VALID_FIXTURE as base.
happy_path = EvalCase(
    case_name="happy_path",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "AI startup financial model."},
    expected_output=VALID_FIXTURE,
    should_pass=True,
)

# ── Edge case ──────────────────────────────────────────────────────────────────
# Exactly 5 assumptions (minimum) and exactly 12 months.
edge_case = EvalCase(
    case_name="edge_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "Minimal financial model."},
    expected_output={
        "revenue_drivers": ["Subscriptions"],
        "cost_buckets": ["Infrastructure"],
        "projection_12_months": [
            {"month": f"Month {i}", "revenue": 1000 * i, "costs": 5000}
            for i in range(1, 13)
        ],
        "assumptions": [
            "ACV is $99/month",
            "10% monthly growth",
            "5% churn",
            "CAC is $100",
            "75% gross margin",
        ],
        "unit_economics": {"ltv": "$594", "cac": "$100"},
        "summary": "",
    },
    should_pass=True,
)

# ── Invalid case ───────────────────────────────────────────────────────────────
# Only 4 assumptions — below the minimum of 5. Schema should reject this.
invalid_case = EvalCase(
    case_name="invalid_case",
    agent_id=AGENT_ID,
    module_key=MODULE_KEY,
    input_fixture={"idea": "Financial model with too few assumptions."},
    expected_output={
        "revenue_drivers": ["Subscriptions"],
        "cost_buckets": ["Infrastructure"],
        "projection_12_months": [
            {"month": f"Month {i}", "revenue": 1000 * i, "costs": 5000}
            for i in range(1, 13)
        ],
        "assumptions": [
            "ACV is $99/month",
            "10% monthly growth",
            "5% churn",
            "CAC is $100",
            # Only 4 assumptions — should fail
        ],
        "unit_economics": {},
        "summary": "Only 4 assumptions — should fail.",
    },
    should_pass=False,
)


def get_cases() -> list[EvalCase]:
    return [happy_path, edge_case, invalid_case]
