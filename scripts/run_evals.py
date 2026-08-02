#!/usr/bin/env python3
"""
FoundrAI AI Evaluation Suite
=============================
Validates all 8 agent output schemas against structured test fixtures,
measures schema validation rates, and reports results.

Usage:
    cd backend && poetry run python ../scripts/run_evals.py
    cd backend && poetry run python ../scripts/run_evals.py --agent idea_validator
    cd backend && poetry run python ../scripts/run_evals.py --verbose

Options:
    --agent AGENT_ID   Run only cases for the specified agent (e.g. idea_validator)
    --verbose          Show detailed error messages for failed cases
    --help             Show this help message and exit

Exit codes:
    0  All cases behaved as expected (including invalid_case failures that correctly detected schema errors)
    1  One or more should_pass=True cases failed schema validation
"""

from __future__ import annotations

import argparse
import sys

# Ensure the project root's parent (i.e. the repo root) is on sys.path
# so that `ai` is importable when running from the backend directory.
import os

# When run as: cd backend && poetry run python ../scripts/run_evals.py
# __file__ = ../scripts/run_evals.py relative to backend/, so we need the parent of scripts/
_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_script_dir)  # /path/to/FoundrAI
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from ai.evaluation.evaluator import SchemaEvaluator
from ai.evaluation.fixtures.all_fixtures import get_all_cases
from ai.evaluation.metrics import compute_summary, format_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FoundrAI AI Evaluation Suite — Schema validation runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--agent",
        metavar="AGENT_ID",
        help="Run only cases for the specified agent (e.g. idea_validator)",
        default=None,
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed error messages for all failed cases",
        default=False,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # Load all cases
    all_cases = get_all_cases()

    # Filter by agent if requested
    if args.agent:
        cases = [c for c in all_cases if c.agent_id == args.agent]
        if not cases:
            available = sorted({c.agent_id for c in all_cases})
            print(f"ERROR: No cases found for agent '{args.agent}'.")
            print(f"Available agents: {', '.join(available)}")
            return 1
        print(f"Running {len(cases)} cases for agent: {args.agent}\n")
    else:
        cases = all_cases
        print(f"Running {len(cases)} total eval cases across {len({c.agent_id for c in cases})} agents\n")

    # Run evaluations
    evaluator = SchemaEvaluator()
    results = evaluator.run_all(cases)

    # Compute summary
    summary = compute_summary(results)

    # Print report
    report = format_report(summary, results)
    print(report)

    # Verbose: show detailed errors
    if args.verbose:
        failed_required = [r for r in results if not r.passed]
        if failed_required:
            print("\n── Detailed Failure Info ──────────────────────────────────────────")
            for r in failed_required:
                print(f"\n[{r.agent_id}] {r.case_name}")
                print(f"  Error: {r.error_msg}")

    # Determine exit code
    # Exit 0 if all cases behaved as expected (should_pass=True cases passed,
    # and should_pass=False cases correctly failed schema validation).
    # Exit 1 if any should_pass=True case failed.
    all_passed = all(r.passed for r in results)

    if all_passed:
        print("\n✓ All eval cases behaved as expected.")
        # Check schema validation rate target
        if summary.schema_valid_rate < 0.85:
            print(
                f"  WARNING: Schema validation rate {summary.schema_valid_rate:.1%} is below the 85% target."
            )
        return 0
    else:
        failed_cases = [r for r in results if not r.passed]
        print(f"\n✗ {len(failed_cases)} case(s) did not behave as expected.")
        for r in failed_cases:
            print(f"  - [{r.agent_id}] {r.case_name}: {r.error_msg[:120]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
