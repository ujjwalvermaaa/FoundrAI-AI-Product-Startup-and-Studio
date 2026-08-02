"""
ai.evaluation.evaluator — Core schema evaluator for FoundrAI AI agents.

EvalCase describes a test scenario.
SchemaEvaluator validates expected_output against the Pydantic schema for
each module_key using get_schema_for_module().
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import ValidationError

from ai.evaluation.metrics import EvalResult
from ai.schemas import get_schema_for_module


@dataclass
class EvalCase:
    """
    A single evaluation test case.

    Attributes:
        case_name:       Human-readable name (e.g. 'happy_path', 'edge_case').
        agent_id:        Agent identifier (e.g. 'idea_validator').
        module_key:      Schema registry key (e.g. 'idea_validation').
        input_fixture:   The inputs to the agent (informational only for schema evals).
        expected_output: The dict that should (or should not) pass schema validation.
        should_pass:     If True, expect schema validation to succeed.
                         If False, expect schema validation to FAIL (invalid input test).
    """

    case_name: str
    agent_id: str
    module_key: str
    input_fixture: dict
    expected_output: dict
    should_pass: bool = True


class SchemaEvaluator:
    """
    Validates EvalCase fixtures against their registered Pydantic schemas.

    For should_pass=True cases:
        - Schema validation must succeed → result.passed=True, result.schema_valid=True
        - Schema validation failure → result.passed=False, result.schema_valid=False

    For should_pass=False cases:
        - Schema validation must FAIL (ValidationError) → result.passed=True, result.schema_valid=False
        - Schema validation succeeds unexpectedly → result.passed=False (test failure — schema didn't catch bad input)
    """

    def run_case(self, case: EvalCase) -> EvalResult:
        """Run a single evaluation case and return an EvalResult."""
        schema_class = get_schema_for_module(case.module_key)

        if schema_class is None:
            return EvalResult(
                agent_id=case.agent_id,
                case_name=case.case_name,
                passed=False,
                error_msg=f"No schema registered for module_key='{case.module_key}'",
                schema_valid=False,
                should_pass=case.should_pass,
            )

        try:
            schema_class(**case.expected_output)
            # Validation succeeded
            if case.should_pass:
                # Expected success — correct outcome
                return EvalResult(
                    agent_id=case.agent_id,
                    case_name=case.case_name,
                    passed=True,
                    error_msg="",
                    schema_valid=True,
                    should_pass=True,
                )
            else:
                # Expected failure but got success — test failure
                return EvalResult(
                    agent_id=case.agent_id,
                    case_name=case.case_name,
                    passed=False,
                    error_msg="Expected schema validation to FAIL for invalid input, but it passed.",
                    schema_valid=True,  # schema said valid, but it should have caught the error
                    should_pass=False,
                )

        except ValidationError as exc:
            # Validation failed
            if case.should_pass:
                # Expected success but got failure — test failure
                return EvalResult(
                    agent_id=case.agent_id,
                    case_name=case.case_name,
                    passed=False,
                    error_msg=str(exc),
                    schema_valid=False,
                    should_pass=True,
                )
            else:
                # Expected failure and got failure — correct outcome (invalid input correctly rejected)
                return EvalResult(
                    agent_id=case.agent_id,
                    case_name=case.case_name,
                    passed=True,
                    error_msg="",
                    schema_valid=False,  # correctly invalid
                    should_pass=False,
                )

        except Exception as exc:
            return EvalResult(
                agent_id=case.agent_id,
                case_name=case.case_name,
                passed=False,
                error_msg=f"Unexpected error: {exc}",
                schema_valid=False,
                should_pass=case.should_pass,
            )

    def run_all(self, cases: list[EvalCase]) -> list[EvalResult]:
        """Run all evaluation cases and return a list of EvalResult objects."""
        return [self.run_case(case) for case in cases]
