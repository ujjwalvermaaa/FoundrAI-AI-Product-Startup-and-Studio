"""
ai.guardrails.prompt_injection — detect and neutralize prompt injection attempts.

Provides functions to identify malicious patterns in user-provided text that
could attempt to hijack or override AI system instructions.
"""

from __future__ import annotations

import re

# ── Injection detection patterns ──────────────────────────────────────────────
# Each pattern is compiled with IGNORECASE | DOTALL where appropriate.

_PATTERNS: list[re.Pattern] = [
    # "ignore previous/prior/all instructions" — allows multi-word qualifiers like "all previous"
    re.compile(r"ignore\s+(previous|prior|all)(\s+(previous|prior|all))?\s+instructions?", re.IGNORECASE),
    # "you are now"
    re.compile(r"you\s+are\s+now\b", re.IGNORECASE),
    # "act as"
    re.compile(r"\bact\s+as\b", re.IGNORECASE),
    # "pretend to be"
    re.compile(r"\bpretend\s+to\s+be\b", re.IGNORECASE),
    # "forget everything/all/previous"
    re.compile(r"\bforget\s+(everything|all|previous)\b", re.IGNORECASE),
    # "system prompt"
    re.compile(r"\bsystem\s+prompt\b", re.IGNORECASE),
    # "jailbreak"
    re.compile(r"\bjailbreak\b", re.IGNORECASE),
    # "DAN" (Do Anything Now) — standalone, case-sensitive to avoid false positives
    re.compile(r"\bDAN\b"),
    # Role injection via newlines: \n\nSYSTEM: / HUMAN: / ASSISTANT: / USER:
    re.compile(r"\n\n(SYSTEM|HUMAN|ASSISTANT|USER)\s*:", re.IGNORECASE),
]

# Pattern for sanitization — same patterns, used with re.sub
_SANITIZE_PATTERNS: list[re.Pattern] = _PATTERNS


def detect_injection(text: str) -> bool:
    """
    Return True if the text appears to contain a prompt injection attempt.

    Checks against known injection patterns including instruction overrides,
    role assumption commands, forget directives, and role-injection via newlines.
    """
    for pattern in _PATTERNS:
        if pattern.search(text):
            return True
    return False


def sanitize_input(text: str) -> str:
    """
    Return a sanitized version of text with injection patterns replaced by [REMOVED].

    Surrounding text is preserved; only the matched injection phrase is replaced.
    """
    sanitized = text
    for pattern in _SANITIZE_PATTERNS:
        sanitized = pattern.sub("[REMOVED]", sanitized)
    return sanitized


def check_idea_brief(idea_brief: str) -> tuple[bool, str]:
    """
    Check idea_brief for injection attempts.

    Returns:
        (is_safe, sanitized_text) where:
        - is_safe: True if no injection detected, False otherwise.
        - sanitized_text: original text if safe, sanitized version if injection found.
    """
    if detect_injection(idea_brief):
        return (False, sanitize_input(idea_brief))
    return (True, idea_brief)
