"""
ai.evaluation.fixtures.all_fixtures — Aggregates all 24 eval cases across 8 agents.

Usage:
    from ai.evaluation.fixtures.all_fixtures import get_all_cases
    cases = get_all_cases()  # Returns all 24 EvalCase objects
"""

from __future__ import annotations

from ai.evaluation.evaluator import EvalCase
from ai.evaluation.fixtures.idea_validator_fixtures import get_cases as idea_validator_cases
from ai.evaluation.fixtures.market_researcher_fixtures import get_cases as market_researcher_cases
from ai.evaluation.fixtures.business_modeler_fixtures import get_cases as business_modeler_cases
from ai.evaluation.fixtures.product_strategist_fixtures import get_cases as product_strategist_cases
from ai.evaluation.fixtures.technical_architect_fixtures import get_cases as technical_architect_cases
from ai.evaluation.fixtures.financial_analyst_fixtures import get_cases as financial_analyst_cases
from ai.evaluation.fixtures.marketing_strategist_fixtures import get_cases as marketing_strategist_cases
from ai.evaluation.fixtures.investor_writer_fixtures import get_cases as investor_writer_cases


def get_all_cases() -> list[EvalCase]:
    """
    Return all 24 evaluation cases across all 8 FoundrAI agents.

    Each agent contributes 3 cases:
    - happy_path:   Valid input, should pass schema validation
    - edge_case:    Edge values (minimums), should pass schema validation
    - invalid_case: Invalid input, schema validation should FAIL (correctly detected)

    Returns:
        List of 24 EvalCase objects in agent order.
    """
    return [
        *idea_validator_cases(),      # idea_validation
        *market_researcher_cases(),   # market_research
        *business_modeler_cases(),    # business_model
        *product_strategist_cases(),  # product_strategy
        *technical_architect_cases(), # technical_architecture
        *financial_analyst_cases(),   # financial_planning
        *marketing_strategist_cases(), # marketing_strategy
        *investor_writer_cases(),     # investor_documentation
    ]
