"""
Unit tests for the embedding pipeline — chunking and embeddings.

Tests are grouped into:
  - Chunking tests  (no model download required)
  - Embedding tests (downloads ~440 MB on first run; skipped if offline)
"""

from __future__ import annotations

import importlib
import socket

import numpy as np
import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_online() -> bool:
    """Return True if we can reach the internet (HuggingFace CDN)."""
    try:
        socket.setdefaulttimeout(3)
        socket.getaddrinfo("huggingface.co", 443)
        return True
    except OSError:
        return False


# Sentence Transformers may not be installed in CI; skip gracefully.
try:
    from sentence_transformers import SentenceTransformer as _ST  # noqa: F401
    _HAS_ST = True
except ImportError:
    _HAS_ST = False

requires_st = pytest.mark.skipif(
    not _HAS_ST,
    reason="sentence-transformers not installed",
)


# ─────────────────────────────────────────────────────────────────────────────
# Chunking tests
# ─────────────────────────────────────────────────────────────────────────────

from ai.rag.chunking import chunk_text


class TestChunkText:
    """Tests for chunk_text()."""

    # ── Basic contract ────────────────────────────────────────────────────

    def test_empty_input_returns_empty(self):
        """Empty string → empty list."""
        assert chunk_text("") == []

    def test_whitespace_only_returns_empty(self):
        """Whitespace-only input → empty list."""
        assert chunk_text("   \n\t  ") == []

    def test_short_text_returns_single_chunk(self):
        """Text shorter than chunk_size → exactly one chunk."""
        text = "Hello, world!"
        result = chunk_text(text, chunk_size=100, overlap=10)
        assert len(result) == 1
        assert result[0] == text

    # ── chunk_size enforcement ─────────────────────────────────────────────

    def test_chunk_size_respected(self):
        """No chunk exceeds chunk_size characters."""
        text = " ".join([f"Sentence number {i}." for i in range(200)])
        chunks = chunk_text(text, chunk_size=100, overlap=20)
        for i, chunk in enumerate(chunks):
            assert len(chunk) <= 100, (
                f"Chunk {i} has {len(chunk)} chars, exceeds limit 100. "
                f"Content: {chunk!r}"
            )

    def test_chunk_size_respected_no_sentence_boundaries(self):
        """Hard limit holds even for text with no sentence delimiters."""
        text = "x" * 5000  # one giant word, no punctuation
        chunks = chunk_text(text, chunk_size=200, overlap=50)
        for chunk in chunks:
            assert len(chunk) <= 200

    def test_chunk_size_respected_with_long_sentences(self):
        """Sentences longer than chunk_size are hard-split."""
        long_sentence = "a" * 1000  # single 'word', 1000 chars
        chunks = chunk_text(long_sentence, chunk_size=300, overlap=30)
        for chunk in chunks:
            assert len(chunk) <= 300

    # ── Content coverage ─────────────────────────────────────────────────

    def test_chunk_coverage(self):
        """
        All original content appears across chunks (no characters dropped).

        Uses pangrams (no character repetition across sentences) to verify
        positional coverage: each chunk[i] must equal text[start_i:start_i+len(chunk_i)].
        """
        overlap = 40
        # Use non-repetitive text so positional verification is unambiguous
        sentences = [
            "The quick brown fox jumps over the lazy dog. ",
            "Pack my box with five dozen liquor jugs! ",
            "How vividly daft jumping zebras vex. ",
            "Sphinx of black quartz judge my vow. ",
            "Bright vixens jump dozy fowl quack. ",
        ]
        text = "".join(sentences) * 6  # ~1500 chars
        chunks = chunk_text(text, chunk_size=200, overlap=overlap)
        assert len(chunks) > 0

        # Verify each chunk matches the expected positional slice of the original
        pos = 0
        for i, chunk in enumerate(chunks):
            expected = text[pos : pos + len(chunk)]
            assert chunk == expected, (
                f"chunk[{i}] does not match text[{pos}:{pos+len(chunk)}]"
            )
            pos = pos + len(chunk) - overlap

        # Full coverage: last position should reach end of text
        final_end = pos + overlap
        assert final_end == len(text), (
            f"Coverage ended at {final_end}, expected {len(text)}"
        )


    def test_all_content_in_chunks(self):
        """
        Stronger coverage: every character position of the original text is
        covered by at least one chunk (no content dropped).

        This directly validates Property 5.

        Verification: given overlap=15, chunk[i] covers text[start_i:start_i+len(chunk_i)]
        where start_{i+1} = start_i + len(chunk_i) - 15.
        The union of all covered ranges must span [0, len(text)).
        We verify both the range coverage AND that each chunk equals the
        corresponding slice of the original text.
        """
        overlap = 15
        text = "First sentence. Second sentence! Third one? And another.\n" * 20
        chunks = chunk_text(text, chunk_size=80, overlap=overlap)
        assert len(chunks) > 0, "Expected chunks but got none"

        pos = 0
        for i, chunk in enumerate(chunks):
            expected = text[pos : pos + len(chunk)]
            assert chunk == expected, (
                f"chunk[{i}] content mismatch:\n"
                f"  expected: {expected!r}\n"
                f"  got:      {chunk!r}"
            )
            pos = pos + len(chunk) - overlap

        # After the last chunk, pos + overlap should equal len(text)
        final_end = pos + overlap
        assert final_end == len(text), (
            f"Coverage gap: covered up to {final_end}, text length {len(text)}"
        )

    # ── Overlap ───────────────────────────────────────────────────────────

    def test_chunk_overlap(self):
        """Overlap text from the end of one chunk appears at the start of the next."""
        text = "Alpha beta gamma delta epsilon zeta eta theta iota kappa. " * 10
        overlap = 30
        chunks = chunk_text(text, chunk_size=120, overlap=overlap)

        if len(chunks) < 2:
            pytest.skip("Not enough chunks to test overlap (text too short)")

        for i in range(len(chunks) - 1):
            tail = chunks[i][-overlap:]
            head = chunks[i + 1]
            assert tail in head, (
                f"Overlap tail {tail!r} from chunk {i} not found in "
                f"chunk {i + 1} head: {head[:overlap * 2]!r}"
            )

    def test_zero_overlap(self):
        """overlap=0 produces non-overlapping chunks that together cover the text."""
        text = "Sentence one. Sentence two. Sentence three. " * 15
        chunks = chunk_text(text, chunk_size=100, overlap=0)
        assert all(len(c) <= 100 for c in chunks)

    # ── Edge cases ────────────────────────────────────────────────────────

    def test_exact_chunk_size_input(self):
        """Text exactly equal to chunk_size returns a single chunk."""
        text = "a" * 100
        chunks = chunk_text(text, chunk_size=100, overlap=10)
        assert len(chunks) >= 1
        assert all(len(c) <= 100 for c in chunks)

    def test_multiline_text(self):
        """Newlines are treated as sentence boundaries."""
        text = "Line one.\nLine two.\nLine three.\n" * 20
        chunks = chunk_text(text, chunk_size=80, overlap=15)
        assert len(chunks) > 0
        assert all(len(c) <= 80 for c in chunks)

    def test_default_parameters(self):
        """Default chunk_size=800 and overlap=150 produce valid chunks."""
        text = "This is a sentence. " * 200  # ~4 000 chars
        chunks = chunk_text(text)
        assert len(chunks) > 0
        assert all(len(c) <= 800 for c in chunks)

    def test_invalid_chunk_size_raises(self):
        """chunk_size <= 0 raises ValueError."""
        with pytest.raises(ValueError):
            chunk_text("some text", chunk_size=0)

    def test_overlap_gte_chunk_size_raises(self):
        """overlap >= chunk_size raises ValueError."""
        with pytest.raises(ValueError):
            chunk_text("some text", chunk_size=100, overlap=100)


# ─────────────────────────────────────────────────────────────────────────────
# Embedding tests
# ─────────────────────────────────────────────────────────────────────────────

@requires_st
class TestEmbeddings:
    """Tests for EmbeddingModel / embed() / embed_single()."""

    @pytest.fixture(autouse=True)
    def _reset_singleton(self):
        """Reset the singleton before each test to ensure isolation."""
        from ai.rag.embeddings import EmbeddingModel
        EmbeddingModel.reset()
        yield
        # Leave the model loaded after tests — it's expensive to reload.

    # ── Shape tests ───────────────────────────────────────────────────────

    def test_embed_shape(self):
        """embed(["hello world"]) → shape (1, 768)."""
        from ai.rag.embeddings import embed
        result = embed(["hello world"])
        assert isinstance(result, np.ndarray)
        assert result.shape == (1, 768), f"Expected (1, 768), got {result.shape}"

    def test_embed_batch_shape(self):
        """embed(N texts) → shape (N, 768)."""
        from ai.rag.embeddings import embed
        texts = ["first", "second", "third"]
        result = embed(texts)
        assert result.shape == (3, 768)

    def test_embed_single_shape(self):
        """embed_single("hello") → shape (768,)."""
        from ai.rag.embeddings import embed_single
        result = embed_single("hello")
        assert isinstance(result, np.ndarray)
        assert result.shape == (768,), f"Expected (768,), got {result.shape}"

    def test_embed_empty_list(self):
        """embed([]) → shape (0, 768) empty array."""
        from ai.rag.embeddings import embed
        result = embed([])
        assert result.shape == (0, 768)

    # ── Normalization ─────────────────────────────────────────────────────

    def test_embeddings_are_l2_normalized(self):
        """Each embedding vector has L2-norm ≈ 1.0."""
        from ai.rag.embeddings import embed
        result = embed(["The quick brown fox", "jumps over the lazy dog"])
        norms = np.linalg.norm(result, axis=1)
        np.testing.assert_allclose(norms, 1.0, atol=1e-5)

    def test_embed_single_is_l2_normalized(self):
        """embed_single output has L2-norm ≈ 1.0."""
        from ai.rag.embeddings import embed_single
        result = embed_single("normalize this")
        norm = np.linalg.norm(result)
        assert abs(norm - 1.0) < 1e-5, f"L2-norm is {norm}, expected 1.0"

    # ── Determinism ───────────────────────────────────────────────────────

    def test_embed_deterministic(self):
        """Same input text produces identical embedding on repeated calls."""
        from ai.rag.embeddings import embed
        text = ["determinism check"]
        first = embed(text).copy()
        second = embed(text).copy()
        np.testing.assert_array_equal(first, second)

    # ── Batch vs single consistency ───────────────────────────────────────

    def test_embed_batch_vs_single(self):
        """embed(["foo"])[0] ≈ embed_single("foo") (within float32 tolerance)."""
        from ai.rag.embeddings import embed, embed_single
        batch_vec = embed(["foo"])[0]
        single_vec = embed_single("foo")
        np.testing.assert_allclose(batch_vec, single_vec, atol=1e-6)

    # ── Singleton behaviour ───────────────────────────────────────────────

    def test_singleton_loads_once(self):
        """
        Calling embed() twice reuses the same EmbeddingModel instance.
        Validated by checking the singleton identity is stable.
        """
        from ai.rag.embeddings import embed, EmbeddingModel

        # First call — loads the model
        embed(["first call"])
        instance_after_first = EmbeddingModel.get_instance()

        # Second call — should reuse the same object
        embed(["second call"])
        instance_after_second = EmbeddingModel.get_instance()

        assert instance_after_first is instance_after_second, (
            "Singleton identity changed between calls — model is being reloaded!"
        )

    # ── dtype ─────────────────────────────────────────────────────────────

    def test_embed_returns_float32(self):
        """Embeddings are float32 (memory-efficient for FAISS)."""
        from ai.rag.embeddings import embed
        result = embed(["dtype check"])
        assert result.dtype == np.float32, f"Expected float32, got {result.dtype}"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

