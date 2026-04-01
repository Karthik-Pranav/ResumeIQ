"""Cosine similarity and score normalisation utilities."""

from __future__ import annotations

import numpy as np


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors.

    If either vector has zero magnitude the similarity is 0.0.

    Args:
        vec_a: First embedding vector.
        vec_b: Second embedding vector.

    Returns:
        A float in the range [-1, 1].
    """
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


def similarity_to_score(similarity: float) -> int:
    """Map a cosine similarity value to a 0–100 match score.

    Cosine similarity for text embeddings typically falls in [0, 1]
    (rarely negative for natural-language pairs).  We clamp to [0, 1]
    and scale linearly to [0, 100].

    Args:
        similarity: Raw cosine similarity value.

    Returns:
        An integer score in the range [0, 100].
    """
    clamped = max(0.0, min(1.0, similarity))
    return int(round(clamped * 100))
