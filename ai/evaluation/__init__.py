"""
ai.evaluation — AI Evaluation Suite for FoundrAI.

Validates all 8 agent output schemas against structured test fixtures,
measures schema validation rates, and provides a standalone eval runner.
"""

from ai.evaluation.evaluator import EvalCase, SchemaEvaluator
from ai.evaluation.metrics import EvalResult, EvalSummary, compute_summary, format_report

__all__ = [
    "EvalCase",
    "SchemaEvaluator",
    "EvalResult",
    "EvalSummary",
    "compute_summary",
    "format_report",
]
