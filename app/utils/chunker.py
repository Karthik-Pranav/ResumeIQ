"""Text chunking utilities for splitting documents into segments.

Splits text at paragraph and sentence boundaries, filters out
trivially short chunks, and returns clean segments for embedding.
"""

from __future__ import annotations

import re


# Minimum character length for a chunk to be worth embedding.
_MIN_CHUNK_LENGTH = 20


def split_into_chunks(text: str) -> list[str]:
    """Split text into meaningful chunks (paragraphs, then sentences).

    Strategy:
        1. Split on double-newlines (paragraph boundaries).
        2. For any paragraph longer than 300 chars, further split on
           sentence-ending punctuation (.!?) followed by whitespace.
        3. Strip each chunk and drop anything shorter than the minimum.

    Args:
        text: The input text to chunk.

    Returns:
        A list of non-empty text chunks.
    """
    # Step 1 — paragraph-level split
    paragraphs = re.split(r"\n{2,}", text.strip())

    chunks: list[str] = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(para) <= 300:
            chunks.append(para)
        else:
            # Step 2 — sentence-level split for long paragraphs
            sentences = re.split(r"(?<=[.!?])\s+", para)
            chunks.extend(s.strip() for s in sentences if s.strip())

    # Step 3 — filter short fragments
    return [c for c in chunks if len(c) >= _MIN_CHUNK_LENGTH]
