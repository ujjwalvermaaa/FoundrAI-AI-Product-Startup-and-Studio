"""
ai.memory — Memory management for FoundrAI.

Provides the MemoryManager orchestrator and artifact-specific helpers.
"""

from ai.memory.artifact_memory import extract_text_from_artifact, get_artifact_content_hash
from ai.memory.memory_manager import MemoryManager, MemorySearchResult

__all__ = [
    "MemoryManager",
    "MemorySearchResult",
    "extract_text_from_artifact",
    "get_artifact_content_hash",
]
