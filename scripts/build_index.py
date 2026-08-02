#!/usr/bin/env python3
"""
Build the FoundrAI knowledge base FAISS index.

Reads all .md files from data/knowledge/, chunks and embeds them,
and saves a combined FAISS index under data/faiss/knowledge/.

Usage:
    cd /Users/ujjwal/Desktop/FoundrAI/backend
    /Users/ujjwal/.local/bin/poetry run python ../scripts/build_index.py

    # With custom paths:
    poetry run python ../scripts/build_index.py \
        --knowledge-dir /path/to/knowledge \
        --output-dir /path/to/faiss/output

    # Dry run (no files written):
    poetry run python ../scripts/build_index.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ── sys.path bootstrap ────────────────────────────────────────────────────────
# Add both the project root and the backend directory so that `import ai`
# and `import app` work whether run from project root, backend/, or scripts/.
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
_BACKEND_DIR = _PROJECT_ROOT / "backend"

if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("build_index")

# ── Constants ─────────────────────────────────────────────────────────────────
PROJECT_KEY = "knowledge"
DEFAULT_KNOWLEDGE_DIR = _PROJECT_ROOT / "data" / "knowledge"
DEFAULT_OUTPUT_DIR = _PROJECT_ROOT / "data" / "faiss" / "knowledge"


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a FAISS knowledge-base index from Markdown files."
    )
    parser.add_argument(
        "--knowledge-dir",
        type=Path,
        default=DEFAULT_KNOWLEDGE_DIR,
        help=f"Root directory for knowledge Markdown files (default: {DEFAULT_KNOWLEDGE_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for FAISS index files (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Read and chunk files but do not write any index files.",
    )
    return parser.parse_args()


# ── Helpers ───────────────────────────────────────────────────────────────────

def discover_documents(knowledge_dir: Path) -> list[Path]:
    """Return all .md files under knowledge_dir, sorted by path."""
    docs = sorted(knowledge_dir.rglob("*.md"))
    logger.info("Found %d Markdown file(s) in %s", len(docs), knowledge_dir)
    return docs


def monkey_patch_faiss_dir(output_dir: Path) -> None:
    """
    Override the FAISS data directory in the indexing module so the index is
    saved to output_dir's parent (since indexing.py appends project_id as a
    subdirectory).

    For PROJECT_KEY = "knowledge", this means:
      output_dir         = data/faiss/knowledge
      faiss data root    = data/faiss
      indexing saves to  = data/faiss/knowledge/index.faiss
    """
    import ai.rag.indexing as indexing_mod

    # The indexing module saves to: _get_faiss_data_dir() / project_id
    # So we patch the root to be output_dir.parent
    faiss_root = output_dir.parent

    def _patched() -> Path:
        return faiss_root

    indexing_mod._get_faiss_data_dir = _patched  # type: ignore[assignment]
    logger.debug("FAISS data root patched to: %s", faiss_root)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()

    knowledge_dir: Path = args.knowledge_dir.resolve()
    output_dir: Path = args.output_dir.resolve()
    dry_run: bool = args.dry_run

    if dry_run:
        logger.info("DRY RUN mode — no files will be written.")

    if not knowledge_dir.exists():
        logger.error("Knowledge directory not found: %s", knowledge_dir)
        sys.exit(1)

    # Patch FAISS dir before importing indexing functions so the right path
    # is used throughout the run.
    if not dry_run:
        monkey_patch_faiss_dir(output_dir)

    from ai.rag.chunking import chunk_text
    from ai.rag.embeddings import embed
    from ai.rag.indexing import (
        add_vectors,
        create_index,
        delete_index,
        index_exists,
        save_index,
    )

    # ── Step 1: Discover documents ────────────────────────────────────────
    md_files = discover_documents(knowledge_dir)
    if not md_files:
        logger.error("No .md files found under %s — nothing to index.", knowledge_dir)
        sys.exit(1)

    # ── Step 2: Idempotency — delete old index before rebuilding ──────────
    if not dry_run:
        if index_exists(PROJECT_KEY):
            logger.info(
                "Existing index found for '%s' — deleting for rebuild.", PROJECT_KEY
            )
            delete_index(PROJECT_KEY)
        create_index(PROJECT_KEY)
        logger.info("Created fresh FAISS index for project key '%s'.", PROJECT_KEY)

    # ── Step 3: Process each document ────────────────────────────────────
    total_chunks = 0
    n_docs = 0

    for md_path in md_files:
        rel_path = md_path.relative_to(knowledge_dir)
        text = md_path.read_text(encoding="utf-8")

        if not text.strip():
            logger.warning("Skipping empty file: %s", rel_path)
            continue

        chunks = chunk_text(text)
        if not chunks:
            logger.warning("No chunks produced for: %s", rel_path)
            continue

        print(f"  {rel_path}: {len(chunks)} chunks")

        if not dry_run:
            # Embed all chunks for this document in one batch
            vectors = embed(chunks)

            # Generate a stable doc_id from the relative path
            doc_id = str(uuid.uuid5(uuid.NAMESPACE_URL, str(rel_path)))

            # Assign a unique chunk ID to each chunk
            chunk_ids = [
                str(uuid.uuid5(uuid.NAMESPACE_URL, f"{doc_id}::{i}"))
                for i in range(len(chunks))
            ]

            add_vectors(PROJECT_KEY, vectors, chunk_ids)

        n_docs += 1
        total_chunks += len(chunks)

    if total_chunks == 0:
        logger.error("No chunks were produced. Index not saved.")
        sys.exit(1)

    # ── Step 4: Save FAISS index ──────────────────────────────────────────
    if not dry_run:
        index_dir = save_index(PROJECT_KEY)
        logger.info("FAISS index saved to: %s", index_dir)
    else:
        logger.info("DRY RUN complete — skipped writing index.")

    # ── Step 5: Summary ───────────────────────────────────────────────────
    print(f"\nSummary:")
    print(f"  Total files:  {n_docs}")
    print(f"  Total chunks: {total_chunks}")
    if not dry_run:
        print(f"  Output path:  {output_dir}")
        print(f"  Index files:  {output_dir / 'index.faiss'}, {output_dir / 'chunk_ids.json'}")
    else:
        print(f"  (dry run — no files written)")


if __name__ == "__main__":
    main()
