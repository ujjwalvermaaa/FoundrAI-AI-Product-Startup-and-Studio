"""
ai.evaluation.fixtures — Structured test fixtures for all 8 FoundrAI AI agents.

Each module provides EvalCase instances for happy_path, edge_case, and invalid_case
test scenarios. Use all_fixtures.get_all_cases() to retrieve all 24 cases.
"""

from ai.evaluation.fixtures.all_fixtures import get_all_cases

__all__ = ["get_all_cases"]
