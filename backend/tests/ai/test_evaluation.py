"""
backend/tests/ai/test_evaluation.py — Pytest integration for the AI evaluation suite.

Imports all 24 eval cases from ai.evaluation.fixtures.all_fixtures and runs
each through SchemaEvaluator, asserting result.passed == True for all cases.

This integrates into the existing pytest suite so `make test-backend` covers
the eval suite automatically.
"""

from __future__ import annotations

import pytest

from ai.evaluation.evaluator import EvalCase, SchemaEvaluator
from ai.evaluation.fixtures.all_fixtures import get_all_cases
from ai.evaluation.metrics import compute_summary


# ── Parametrize all 24 cases ───────────────────────────────────────────────────
def _make_case_id(case: EvalCase) -> str:
    """Build a readable pytest case ID: agent_id::case_name."""
    return f"{case.agent_id}::{case.case_name}"


ALL_CASES = get_all_cases()

evaluator = SchemaEvaluator()


@pytest.mark.parametrize("case", ALL_CASES, ids=[_make_case_id(c) for c in ALL_CASES])
def test_eval_case(case: EvalCase) -> None:
    """
    Each eval case should behave as expected:
    - should_pass=True  → schema validation must succeed
    - should_pass=False → schema validation must FAIL (invalid input correctly rejected)

    result.passed=True means "the case behaved as expected" in both scenarios.
    """
    result = evaluator.run_case(case)

    assert result.passed, (
        f"Eval case FAILED: [{result.agent_id}] {result.case_name}\n"
        f"  should_pass={case.should_pass}\n"
        f"  error_msg={result.error_msg}"
    )


# ── Summary-level test ─────────────────────────────────────────────────────────

def test_eval_summary_schema_valid_rate() -> None:
    """
    The overall schema validation rate for should_pass=True cases must be ≥ 85%.
    """
    results = evaluator.run_all(ALL_CASES)
    summary = compute_summary(results)

    # should_pass=True cases: 16 cases (8 agents × 2: happy_path + edge_case)
    should_pass_true_cases = [c for c in ALL_CASES if c.should_pass]
    should_pass_true_results = [r for r in results if any(
        r.agent_id == c.agent_id and r.case_name == c.case_name
        for c in should_pass_true_cases
    )]

    passed_required = sum(1 for r in should_pass_true_results if r.passed)
    total_required = len(should_pass_true_cases)
    rate = passed_required / total_required if total_required > 0 else 0.0

    assert rate >= 0.85, (
        f"Schema validation rate {rate:.1%} is below the 85% target. "
        f"Passed {passed_required}/{total_required} should_pass=True cases."
    )


def test_eval_total_case_count() -> None:
    """Ensure all 24 cases are present (8 agents × 3 cases each)."""
    assert len(ALL_CASES) == 24, f"Expected 24 eval cases, got {len(ALL_CASES)}"


def test_eval_agent_coverage() -> None:
    """Ensure all 8 agents are covered in the eval suite."""
    expected_agents = {
        "idea_validator",
        "market_researcher",
        "business_modeler",
        "product_strategist",
        "technical_architect",
        "financial_analyst",
        "marketing_strategist",
        "investor_writer",
    }
    actual_agents = {c.agent_id for c in ALL_CASES}
    assert actual_agents == expected_agents, (
        f"Missing agents: {expected_agents - actual_agents}. "
        f"Unexpected agents: {actual_agents - expected_agents}."
    )


def test_eval_invalid_cases_detected() -> None:
    """All should_pass=False (invalid_case) fixtures must be correctly rejected by the schema."""
    invalid_cases = [c for c in ALL_CASES if not c.should_pass]
    assert len(invalid_cases) == 8, f"Expected 8 invalid cases, got {len(invalid_cases)}"

    for case in invalid_cases:
        result = evaluator.run_case(case)
        assert result.passed, (
            f"Invalid case not properly detected: [{case.agent_id}] {case.case_name}. "
            f"Schema should have rejected the input but it passed."
        )
        assert not result.schema_valid, (
            f"Invalid case should have schema_valid=False: [{case.agent_id}] {case.case_name}"
        )
