"""
Artifact-specific memory helpers.

Provides utilities for extracting indexable text from artifact JSON content
and computing content hashes for deduplication.
"""

from __future__ import annotations

import hashlib


def extract_text_from_artifact(content_json: dict, artifact_type: str) -> str:
    """
    Concatenate all string leaf-values from the artifact JSON into indexable text.

    Recursively walks the JSON structure and collects all string values,
    joining them with newlines. The artifact_type is prepended as context.

    Args:
        content_json:  The artifact's content dictionary.
        artifact_type: The type/name of the artifact (prepended for context).

    Returns:
        A single string of all text content suitable for chunking and indexing.
    """
    parts: list[str] = [artifact_type]

    def _collect(obj: object) -> None:
        if isinstance(obj, str):
            stripped = obj.strip()
            if stripped:
                parts.append(stripped)
        elif isinstance(obj, dict):
            for value in obj.values():
                _collect(value)
        elif isinstance(obj, list):
            for item in obj:
                _collect(item)
        # Numbers / booleans / None are ignored

    _collect(content_json)
    return "\n".join(parts)


def get_artifact_content_hash(content_text: str) -> str:
    """
    Return the SHA-256 hex digest of the given content text.

    Args:
        content_text: The text to hash.

    Returns:
        64-character lowercase hex string.
    """
    return hashlib.sha256(content_text.encode("utf-8")).hexdigest()
