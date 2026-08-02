"""
ai.guardrails — public API for FoundrAI guardrail modules.

Provides three layers of protection:
  - prompt_injection: detect and neutralize LLM prompt injection attempts
  - schema_validation: domain-level business rule checks beyond Pydantic
  - output_validation: post-generation quality checks on AI artifact output
"""

from ai.guardrails.output_validation import check_output_quality
from ai.guardrails.prompt_injection import check_idea_brief, detect_injection, sanitize_input
from ai.guardrails.schema_validation import validate_artifact_content

__all__ = [
    "detect_injection",
    "sanitize_input",
    "check_idea_brief",
    "validate_artifact_content",
    "check_output_quality",
]
