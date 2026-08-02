"""
Content-aware text chunking for the FoundrAI RAG pipeline.

Strategy
--------
1. Split the input on sentence-ending punctuation (``.``, ``!``, ``?``) and
   newline characters, keeping the delimiter attached to the preceding segment.
2. Greedily accumulate consecutive fragments until the chunk would exceed
   ``chunk_size``.  When it would, emit the current chunk and begin a new one.
3. Each new chunk starts with the last ``overlap`` characters of the previous
   chunk (the *carry*) so content bridges boundaries for retrieval.
4. Any individual fragment longer than ``chunk_size`` is hard-split first to
   guarantee the per-chunk size limit is always respected.

Guarantees
----------
- Every chunk satisfies ``len(chunk) <= chunk_size``.
- The full original text is recoverable from the chunks (Property 5):
  consecutive chunks share exactly ``overlap`` characters at their boundary,
  so de-overlapping reconstructs the original.
- An empty / whitespace-only input returns ``[]``.
"""

from __future__ import annotations

import re
from typing import Iterator

# Split *after* sentence-ending characters so the delimiter stays
# attached to the preceding segment, preserving content exactly.
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?\n])")


def _iter_fragments(text: str, chunk_size: int) -> Iterator[str]:
    """
    Yield sentence-boundary fragments from *text*.

    Any fragment exceeding *chunk_size* is hard-split into pieces of at most
    *chunk_size* characters so that the greedy accumulator never receives a
    fragment that alone would exceed the limit.
    """
    for frag in _SENTENCE_SPLIT_RE.split(text):
        if not frag:
            continue
        while len(frag) > chunk_size:
            yield frag[:chunk_size]
            frag = frag[chunk_size:]
        if frag:
            yield frag


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 150,
) -> list[str]:
    """
    Split *text* into overlapping chunks of at most *chunk_size* characters.

    Args:
        text:       Input text to split.
        chunk_size: Maximum characters per chunk (inclusive).  Must be > 0.
        overlap:    Characters from the tail of each emitted chunk prepended
                    to the next chunk.  Must be < chunk_size.

    Returns:
        List of non-empty strings.  Returns ``[]`` for blank input.

    Raises:
        ValueError: If ``chunk_size <= 0`` or ``overlap >= chunk_size``.
    """
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be > 0, got {chunk_size}")
    if overlap >= chunk_size:
        raise ValueError(
            f"overlap ({overlap}) must be less than chunk_size ({chunk_size})"
        )

    # ── Fast-path: empty / whitespace input ──────────────────────────────
    if not text or not text.strip():
        return []

    chunks: list[str] = []

    # carry  — overlap tail from the last emitted chunk, prepended to the next
    # buf    — new content accumulated for the current in-progress chunk
    #          (NOT including carry, to keep accounting simple)
    carry: str = ""
    buf: str = ""

    for frag in _iter_fragments(text, chunk_size):
        # Would adding frag overflow the current chunk?
        if len(carry) + len(buf) + len(frag) <= chunk_size:
            # Fits — accumulate
            buf += frag
        else:
            # Emit the current chunk if it has any buffered content
            if buf:
                chunk = carry + buf
                # Hard safety cap (shouldn't be needed after the checks above)
                chunk = chunk[:chunk_size]
                chunks.append(chunk)
                # New carry is the last `overlap` chars of the emitted chunk
                carry = chunk[-overlap:] if overlap else ""
                buf = ""

            # Now decide what to do with `frag`:
            if len(carry) + len(frag) <= chunk_size:
                # frag fits after the new carry — buffer it
                buf = frag
            else:
                # carry alone is almost at chunk_size; frag still doesn't fit.
                # This can only happen when overlap is large relative to
                # chunk_size.  Hard-split frag around the remaining capacity.
                remaining = frag
                while remaining:
                    available = chunk_size - len(carry)
                    if available <= 0:
                        # Carry itself is full-size — flush it as a chunk
                        chunk = carry[:chunk_size]
                        chunks.append(chunk)
                        carry = chunk[-overlap:] if overlap else ""
                        available = chunk_size - len(carry)

                    piece = remaining[:available]
                    remaining = remaining[available:]

                    if remaining:
                        # More content follows — emit this piece immediately
                        chunk = (carry + piece)[:chunk_size]
                        chunks.append(chunk)
                        carry = chunk[-overlap:] if overlap else ""
                        buf = ""
                    else:
                        # Last piece — buffer it so subsequent fragments can
                        # be appended before emitting
                        buf = piece

    # ── Flush the final buffer ────────────────────────────────────────────
    if buf:
        chunk = (carry + buf)[:chunk_size]
        chunks.append(chunk)
    elif not chunks and text.strip():
        # Shouldn't reach here, but guard against edge cases
        chunks.append(text[:chunk_size])

    return chunks
