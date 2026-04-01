"""Semantic skill presence detection using sentence-transformer embeddings.

Replaces the old exact-string keyword matching with an embedding-based approach:

For each extracted skill (e.g. "machine learning"):
  1. Embed the skill phrase.
  2. Compare against embeddings of every resume sentence.
  3. A skill is considered PRESENT if max cosine similarity ≥ threshold.

Threshold is read from the ``SKILL_THRESHOLD`` environment variable
(default 0.45), so it can be tuned without code changes.

Why 0.45?
---------
For all-MiniLM-L6-v2, pairs like ("machine learning", "ML techniques")
score ~0.62, while unrelated pairs score < 0.25.  0.45 is comfortably
above the noise floor while still catching semantic synonyms.

Performance notes
-----------------
* Skills and resume sentences are embedded in two batch calls — O(1) model
  round-trips regardless of input size.
* Similarity matrix is computed via batched dot product (embeddings are
  already L2-normalised by the model).
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

import numpy as np

from app.utils.chunker import split_into_chunks
from app.utils.embedding import get_embeddings_batch

logger = logging.getLogger(__name__)

# ── Threshold (env-configurable) ─────────────────────────────────────────────

def _load_threshold() -> float:
    """Read SKILL_THRESHOLD from env, falling back to 0.45."""
    raw = os.environ.get("SKILL_THRESHOLD", "0.45")
    try:
        value = float(raw)
        if not 0.0 <= value <= 1.0:
            raise ValueError
        return value
    except ValueError:
        logger.warning(
            "Invalid SKILL_THRESHOLD=%r; using default 0.45", raw
        )
        return 0.45


SKILL_PRESENT_THRESHOLD: float = _load_threshold()

# Maximum items returned in each list
MAX_STRENGTHS: int = 6
MAX_GAPS: int = 6

# Minimum character length for a resume sentence to be worth embedding
_MIN_SENTENCE_LEN: int = 15


# ── Output dataclass ──────────────────────────────────────────────────────────

@dataclass
class SemanticMatchResult:
    """Result of semantic skill-presence detection."""

    strengths: list[str]
    """Human-readable strength strings, e.g. 'machine learning (score: 0.78)'."""

    gaps: list[str]
    """Human-readable gap strings, e.g. 'kubernetes'."""


# ── Public API ────────────────────────────────────────────────────────────────

def semantic_skill_match(
    skills: list[str],
    resume_text: str,
    *,
    top_n: int = MAX_STRENGTHS,
) -> SemanticMatchResult:
    """Check which skills from *skills* are semantically present in *resume_text*.

    Args:
        skills:       Flat list of skill phrases to check (from ExtractedKeywords).
        resume_text:  Full plain-text resume content.
        top_n:        Cap on returned strengths and gaps each.

    Returns:
        A SemanticMatchResult.
    """
    if not skills:
        return SemanticMatchResult(strengths=[], gaps=[])

    # Split resume into sentences; fall back to the whole text if chunking fails
    sentences = [
        s for s in split_into_chunks(resume_text)
        if len(s) >= _MIN_SENTENCE_LEN
    ]
    if not sentences:
        sentences = [resume_text[:2000]]  # safety fallback

    logger.debug(
        "Semantic skill match: %d skills × %d resume sentences (threshold %.2f)",
        len(skills), len(sentences), SKILL_PRESENT_THRESHOLD,
    )

    # Batch-embed skills and resume sentences
    skill_embs = get_embeddings_batch(skills)       # (S, D)
    sent_embs  = get_embeddings_batch(sentences)    # (N, D)

    # Similarity matrix: (S, N) — embeddings are L2-normalised → dot = cosine
    sim_matrix: np.ndarray = skill_embs @ sent_embs.T

    # Best resume-sentence similarity per skill
    best_sim_per_skill: np.ndarray = sim_matrix.max(axis=1)  # (S,)

    strengths: list[tuple[str, float]] = []
    gaps: list[str] = []

    for skill, best_sim in zip(skills, best_sim_per_skill.tolist()):
        if best_sim >= SKILL_PRESENT_THRESHOLD:
            strengths.append((skill, best_sim))
        else:
            gaps.append(skill)

    # Sort strengths by descending similarity so the best matches appear first
    strengths.sort(key=lambda t: t[1], reverse=True)

    strength_strings = [
        f"{skill.title()} — strong match (score: {sim:.2f})"
        for skill, sim in strengths[:top_n]
    ]
    gap_strings = gaps[:top_n]

    return SemanticMatchResult(strengths=strength_strings, gaps=gap_strings)
