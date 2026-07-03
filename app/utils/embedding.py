"""Text embedding utilities using sentence-transformers.

Loads the all-MiniLM-L6-v2 model once at module level and exposes
a function to encode text into dense vector embeddings.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """Load and cache the sentence-transformer model (singleton)."""
    logger.info("Loading sentence-transformer model '%s' …", MODEL_NAME)
    return SentenceTransformer(MODEL_NAME)


def get_embedding(text: str) -> np.ndarray:
    """Encode a text string into a normalised embedding vector.

    Args:
        text: The input text to encode.

    Returns:
        A 1-D numpy array (float32) representing the text embedding.
    """
    model = _get_model()
    embedding: np.ndarray = model.encode(text, normalize_embeddings=True)
    return embedding


def get_embeddings_batch(texts: list[str]) -> np.ndarray:
    """Encode multiple texts in a single forward pass.

    Args:
        texts: List of input strings to encode.

    Returns:
        A 2-D numpy array of shape (len(texts), embedding_dim).
    """
    model = _get_model()
    embeddings: np.ndarray = model.encode(texts, normalize_embeddings=True)
    return embeddings
