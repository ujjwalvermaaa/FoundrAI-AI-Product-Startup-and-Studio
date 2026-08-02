"""
ai.guardrails.output_validation — post-generation quality checks for AI artifact output.

Verifies generated content is complete, relevant, and free of placeholder text.
"""

from __future__ import annotations

import re

# ── Placeholder patterns ───────────────────────────────────────────────────────
# Matches {{anything}}, [TODO], [PLACEHOLDER], or a bare "TBD" string value.
_PLACEHOLDER_RE = re.compile(
    r"\{\{.*?\}\}"      # Mustache-style: {{placeholder}}
    r"|\[TODO\]"         # [TODO]
    r"|\[PLACEHOLDER\]", # [PLACEHOLDER]
    re.IGNORECASE,
)

# Stopwords to exclude from brief relevance comparison
_STOPWORDS: frozenset[str] = frozenset(
    ["a", "the", "is", "in", "to", "of", "for", "and", "an", "on", "at",
     "be", "it", "this", "that", "with", "by", "from", "or", "are", "was",
     "as", "we", "our", "its", "my", "i", "you", "he", "she", "they", "not",
     "but", "so", "if", "do", "have", "has"]
)


def _extract_strings(obj: object, path: str = "") -> list[tuple[str, str]]:
    """
    Recursively walk a dict/list structure and yield (field_path, string_value) pairs.

    Used to locate placeholder text in nested artifact content.
    """
    results: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            child_path = f"{path}.{key}" if path else key
            results.extend(_extract_strings(value, child_path))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            child_path = f"{path}[{idx}]"
            results.extend(_extract_strings(item, child_path))
    elif isinstance(obj, str):
        results.append((path, obj))
    return results


def check_for_placeholders(content: dict) -> list[str]:
    """
    Return a list of field paths that contain unresolved placeholder text.

    Detects: {{...}}, [TODO], [PLACEHOLDER].
    A field value of exactly "TBD" (case-insensitive) is also flagged.
    """
    flagged: list[str] = []
    for field_path, value in _extract_strings(content):
        if _PLACEHOLDER_RE.search(value):
            flagged.append(field_path)
        elif value.strip().upper() == "TBD":
            flagged.append(field_path)
    return flagged


def check_brief_relevance(content: dict, idea_brief: str) -> bool:
    """
    Return True if at least 2 significant words from idea_brief appear in the output.

    Tokenizes both the brief and all string values in content (lowercased),
    removes stopwords, then checks for ≥2 token overlaps.
    """
    def tokenize(text: str) -> set[str]:
        tokens = re.split(r"\W+", text.lower())
        return {t for t in tokens if t and t not in _STOPWORDS and len(t) > 2}

    brief_tokens = tokenize(idea_brief)
    if not brief_tokens:
        return False

    # Collect all string values from the content dict
    output_text = " ".join(value for _, value in _extract_strings(content))
    output_tokens = tokenize(output_text)

    overlap = brief_tokens & output_tokens
    return len(overlap) >= 2


def check_output_quality(
    content: dict,
    artifact_type: str,
    idea_brief: str,
) -> tuple[bool, list[str]]:
    """
    Run quality checks on generated artifact content.

    Returns:
        (passes, warnings) where passes is True if all checks pass,
        and warnings is a list of human-readable warning messages.

    Checks performed:
        1. No placeholder text left ({{...}}, [TODO], [PLACEHOLDER], bare TBD)
        2. No obviously truncated content (strings ending with "...")
        3. Numeric fields within reasonable ranges (validation_score 0-100)
        4. Brief relevance: at least 2 words from idea_brief appear in output
    """
    warnings: list[str] = []

    # ── Check 1: Placeholder text ─────────────────────────────────────────────
    placeholder_fields = check_for_placeholders(content)
    for field_path in placeholder_fields:
        warnings.append(f"Unresolved placeholder in field: {field_path}")

    # ── Check 2: Truncated content ────────────────────────────────────────────
    for field_path, value in _extract_strings(content):
        stripped = value.rstrip()
        if stripped.endswith("..."):
            warnings.append(f"Possibly truncated content in field: {field_path}")

    # ── Check 3: Numeric range validation ─────────────────────────────────────
    score = content.get("validation_score")
    if score is not None and isinstance(score, (int, float)):
        if not (0 <= score <= 100):
            warnings.append(
                f"validation_score out of range [0, 100]: {score}"
            )

    # ── Check 4: Brief relevance ──────────────────────────────────────────────
    if idea_brief and not check_brief_relevance(content, idea_brief):
        warnings.append(
            "Output may not be relevant to the provided idea brief "
            "(fewer than 2 significant words overlap)"
        )

    return (len(warnings) == 0, warnings)
