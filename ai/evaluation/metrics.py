"""
ai.evaluation.metrics — Evaluation result dataclasses and reporting utilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvalResult:
    """Result of a single evaluation case."""

    agent_id: str
    case_name: str
    passed: bool  # True means "behaved as expected" (both valid pass and invalid-correctly-failing)
    error_msg: str = ""
    schema_valid: bool = False  # True only when schema validation succeeded
    should_pass: bool = True  # mirrors EvalCase.should_pass — used to compute schema_valid_rate


@dataclass
class EvalSummary:
    """Aggregated metrics across all eval cases."""

    total: int
    passed: int
    failed: int
    schema_valid_count: int
    schema_valid_rate: float  # fraction of should_pass=True cases that passed


def compute_summary(results: list[EvalResult]) -> EvalSummary:
    """
    Compute aggregate metrics from a list of EvalResult objects.

    schema_valid_rate = (# of should_pass=True cases that passed) / (# of should_pass=True cases)

    This measures how well the happy_path and edge_case fixtures validate, targeting ≥85%.
    The should_pass=False (invalid_case) fixtures are excluded from the rate because their
    correct outcome is a validation failure, not a success.
    """
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    schema_valid_count = sum(1 for r in results if r.schema_valid)

    # Rate: passing should_pass=True cases / total should_pass=True cases
    should_pass_true = [r for r in results if r.should_pass]
    should_pass_true_passed = sum(1 for r in should_pass_true if r.passed)
    total_should_pass_true = len(should_pass_true)
    schema_valid_rate = (
        should_pass_true_passed / total_should_pass_true
        if total_should_pass_true > 0
        else 0.0
    )

    return EvalSummary(
        total=total,
        passed=passed,
        failed=failed,
        schema_valid_count=schema_valid_count,
        schema_valid_rate=schema_valid_rate,
    )


def format_report(summary: EvalSummary, results: list[EvalResult]) -> str:
    """
    Format a human-readable evaluation report.

    Shows per-agent results table + overall metrics.
    """
    lines: list[str] = []

    lines.append("=" * 70)
    lines.append("  FoundrAI AI Evaluation Suite — Results Report")
    lines.append("=" * 70)
    lines.append("")

    # Group results by agent
    agents: dict[str, list[EvalResult]] = {}
    for result in results:
        agents.setdefault(result.agent_id, []).append(result)

    # Per-agent table
    lines.append(f"{'Agent':<30} {'Case':<25} {'Status':<10} {'Schema'}")
    lines.append("-" * 70)

    for agent_id, agent_results in agents.items():
        for r in agent_results:
            status = "PASS" if r.passed else "FAIL"
            schema = "valid" if r.schema_valid else ("invalid ✓" if r.passed and not r.schema_valid else "invalid ✗")
            lines.append(f"{agent_id:<30} {r.case_name:<25} {status:<10} {schema}")
            if not r.passed and r.error_msg:
                lines.append(f"  {'':>30} ↳ {r.error_msg}")
        lines.append("")

    # Overall metrics
    lines.append("=" * 70)
    lines.append("  Overall Metrics")
    lines.append("=" * 70)
    lines.append(f"  Total cases:          {summary.total}")
    lines.append(f"  Passed:               {summary.passed}")
    lines.append(f"  Failed:               {summary.failed}")
    lines.append(f"  Schema-valid count:   {summary.schema_valid_count}")
    lines.append(f"  Schema-valid rate:    {summary.schema_valid_rate:.1%}")
    lines.append("")

    target_met = summary.schema_valid_rate >= 0.85
    target_label = "✓ TARGET MET (≥85%)" if target_met else "✗ BELOW TARGET (<85%)"
    lines.append(f"  {target_label}")
    lines.append("=" * 70)

    return "\n".join(lines)
