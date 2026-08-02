"""
ai.guardrails.schema_validation — domain-level business rule checks beyond Pydantic.

Applies artifact-type-specific validation rules that enforce minimum cardinality,
required field presence, and structural completeness.
"""

from __future__ import annotations

# ── 9 required BMC blocks ─────────────────────────────────────────────────────
_BMC_BLOCKS: list[str] = [
    "value_proposition",
    "customer_segments",
    "channels",
    "customer_relationships",
    "revenue_streams",
    "key_resources",
    "key_activities",
    "key_partnerships",
    "cost_structure",
]


def validate_non_empty_fields(content: dict, required_fields: list[str]) -> list[str]:
    """
    Return a list of field names that are missing or empty in content.

    A field is considered empty if its value is None, an empty string, or an empty list.
    """
    missing: list[str] = []
    for field in required_fields:
        value = content.get(field)
        if value is None:
            missing.append(field)
        elif isinstance(value, (str, list)) and len(value) == 0:
            missing.append(field)
    return missing


def validate_min_array_length(content: dict, field: str, min_len: int) -> bool:
    """
    Return True if content[field] is a list with at least min_len items.

    Returns False if the field is missing, not a list, or has fewer than min_len items.
    """
    value = content.get(field)
    if not isinstance(value, list):
        return False
    return len(value) >= min_len


def _validate_validation_report(content: dict) -> list[str]:
    """Validation rules for validation_report artifact type."""
    errors: list[str] = []

    # risks >= 3
    if not validate_min_array_length(content, "risks", 3):
        risks = content.get("risks", [])
        count = len(risks) if isinstance(risks, list) else 0
        errors.append(f"validation_report requires at least 3 risks; got {count}")

    # validation_score 0-100
    score = content.get("validation_score")
    if score is None:
        errors.append("validation_report requires validation_score field")
    elif not isinstance(score, (int, float)) or not (0 <= score <= 100):
        errors.append(f"validation_score must be between 0 and 100; got {score!r}")

    # non-empty summary
    missing = validate_non_empty_fields(content, ["summary"])
    for f in missing:
        errors.append(f"validation_report requires non-empty field: {f}")

    return errors


def _validate_market_analysis(content: dict) -> list[str]:
    """Validation rules for market_analysis artifact type."""
    errors: list[str] = []

    # competitors >= 3
    if not validate_min_array_length(content, "competitors", 3):
        competitors = content.get("competitors", [])
        count = len(competitors) if isinstance(competitors, list) else 0
        errors.append(f"market_analysis requires at least 3 competitors; got {count}")

    # non-empty summary
    missing = validate_non_empty_fields(content, ["summary"])
    for f in missing:
        errors.append(f"market_analysis requires non-empty field: {f}")

    # TAM/SAM/SOM present
    for field in ["tam", "sam", "som"]:
        if content.get(field) is None:
            errors.append(f"market_analysis requires field: {field}")

    return errors


def _validate_business_model_canvas(content: dict) -> list[str]:
    """Validation rules for business_model_canvas artifact type."""
    errors: list[str] = []

    for block in _BMC_BLOCKS:
        value = content.get(block)
        if value is None:
            errors.append(f"business_model_canvas missing required block: {block}")
        elif isinstance(value, str) and value.strip() == "":
            errors.append(f"business_model_canvas block '{block}' must not be empty")
        elif isinstance(value, list) and len(value) == 0:
            errors.append(f"business_model_canvas block '{block}' must not be empty")

    return errors


def _validate_product_roadmap(content: dict) -> list[str]:
    """Validation rules for product_roadmap artifact type."""
    errors: list[str] = []

    if not validate_min_array_length(content, "phases", 2):
        phases = content.get("phases", [])
        count = len(phases) if isinstance(phases, list) else 0
        errors.append(f"product_roadmap requires at least 2 phases; got {count}")

    return errors


def _validate_financial_model(content: dict) -> list[str]:
    """Validation rules for financial_model artifact type."""
    errors: list[str] = []

    if not validate_min_array_length(content, "assumptions", 5):
        assumptions = content.get("assumptions", [])
        count = len(assumptions) if isinstance(assumptions, list) else 0
        errors.append(f"financial_model requires at least 5 assumptions; got {count}")

    return errors


def _validate_marketing_plan(content: dict) -> list[str]:
    """Validation rules for marketing_plan artifact type."""
    errors: list[str] = []

    # channels >= 3
    if not validate_min_array_length(content, "channels", 3):
        channels = content.get("channels", [])
        count = len(channels) if isinstance(channels, list) else 0
        errors.append(f"marketing_plan requires at least 3 channels; got {count}")

    # launch_checklist >= 5
    if not validate_min_array_length(content, "launch_checklist", 5):
        checklist = content.get("launch_checklist", [])
        count = len(checklist) if isinstance(checklist, list) else 0
        errors.append(f"marketing_plan requires at least 5 launch_checklist items; got {count}")

    return errors


def _validate_investor_deck_outline(content: dict) -> list[str]:
    """Validation rules for investor_deck_outline artifact type."""
    errors: list[str] = []

    if not validate_min_array_length(content, "slides", 10):
        slides = content.get("slides", [])
        count = len(slides) if isinstance(slides, list) else 0
        errors.append(f"investor_deck_outline requires at least 10 slides; got {count}")

    return errors


def _validate_architecture_doc(content: dict) -> list[str]:
    """Validation rules for architecture_doc artifact type."""
    errors: list[str] = []

    # components present (non-None, non-empty)
    components = content.get("components")
    if components is None:
        errors.append("architecture_doc requires field: components")
    elif isinstance(components, list) and len(components) == 0:
        errors.append("architecture_doc components must not be empty")

    # security_considerations present
    security = content.get("security_considerations")
    if security is None:
        errors.append("architecture_doc requires field: security_considerations")
    elif isinstance(security, str) and security.strip() == "":
        errors.append("architecture_doc security_considerations must not be empty")
    elif isinstance(security, list) and len(security) == 0:
        errors.append("architecture_doc security_considerations must not be empty")

    return errors


# ── Dispatch table ─────────────────────────────────────────────────────────────
_VALIDATORS = {
    "validation_report": _validate_validation_report,
    "market_analysis": _validate_market_analysis,
    "business_model_canvas": _validate_business_model_canvas,
    "product_roadmap": _validate_product_roadmap,
    "financial_model": _validate_financial_model,
    "marketing_plan": _validate_marketing_plan,
    "investor_deck_outline": _validate_investor_deck_outline,
    "architecture_doc": _validate_architecture_doc,
}


def validate_artifact_content(
    artifact_type: str,
    content: dict,
) -> tuple[bool, list[str]]:
    """
    Apply domain-level validation rules for a specific artifact type.

    Returns:
        (is_valid, errors) where is_valid is True if no errors were found,
        and errors is a list of human-readable error messages.

    Supported artifact types:
        validation_report, market_analysis, business_model_canvas,
        product_roadmap, financial_model, marketing_plan,
        investor_deck_outline, architecture_doc.

    Unknown artifact types return (True, []) — no rules to violate.
    """
    validator = _VALIDATORS.get(artifact_type)
    if validator is None:
        return (True, [])

    errors = validator(content)
    return (len(errors) == 0, errors)
