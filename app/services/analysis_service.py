"""Resume analysis service — business logic layer.

Uses sentence-transformer embeddings for semantic similarity scoring,
keyword-based extraction for strengths / gaps, and chunk-level
matching to surface the most relevant resume sections.

Intelligence upgrade (v2)
--------------------------
* Weak/vague JDs are expanded before embedding comparison, so the
  overall score reflects the full role profile rather than a 2-word phrase.
* Strengths and gaps use embedding-based detection (not exact string match).
* Top-3 matched sections are always returned even on moderate similarity.
* The response carries optional explanation metadata (jd_warning,
  matched_role, keyword_breakdown) for the UI.
"""

from __future__ import annotations

import logging

import numpy as np

from app.models.schemas import AnalysisResponse, MatchedSection
from app.utils.chunker import split_into_chunks
from app.utils.embedding import get_embedding, get_embeddings_batch
from app.utils.keyword_analysis import analyze_keywords
from app.utils.similarity import cosine_similarity, similarity_to_score

logger = logging.getLogger(__name__)

# Number of top resume chunks to return in the response.
_TOP_K_SECTIONS = 3


async def analyze_resume(resume_text: str, job_description: str) -> AnalysisResponse:
    """Analyse a resume against a job description.

    Args:
        resume_text:     Plain-text content extracted from the resume PDF.
        job_description: The target job description to compare against.

    Returns:
        An AnalysisResponse with match_score, strengths, gaps,
        matched_sections, and optional explanation metadata.
    """
    # Step 1 — keyword analysis (includes JD expansion + semantic matching)
    kw_result = analyze_keywords(resume_text, job_description, top_n=6)

    # Step 2 — use the (possibly expanded) JD for the overall embedding score
    expansion = kw_result.jd_expansion
    effective_jd = expansion.expanded_jd if expansion else job_description
    match_score = _compute_score(resume_text, effective_jd)

    # Step 3 — chunk-level matched sections (always ≥ top-3)
    matched_sections = _find_matched_sections(resume_text, effective_jd)

    # Step 4 — build explanation metadata
    jd_warning: str | None = expansion.warning if expansion else None
    matched_role: str | None = expansion.matched_role if expansion else None
    keyword_breakdown: dict | None = (
        kw_result.extracted_keywords.to_dict()
        if kw_result.extracted_keywords
        else None
    )

    return AnalysisResponse(
        match_score=match_score,
        strengths=kw_result.strengths,
        gaps=kw_result.gaps,
        matched_sections=matched_sections,
        jd_warning=jd_warning,
        matched_role=matched_role,
        keyword_breakdown=keyword_breakdown,
    )


def _compute_score(resume_text: str, job_description: str) -> int:
    """Compute a 0–100 match score using embedding cosine similarity."""
    resume_emb = get_embedding(resume_text)
    jd_emb = get_embedding(job_description)
    raw_sim = cosine_similarity(resume_emb, jd_emb)
    score = similarity_to_score(raw_sim)
    logger.info("Semantic similarity: %.4f → score: %d", raw_sim, score)
    return score


def _find_matched_sections(
    resume_text: str,
    job_description: str,
) -> list[MatchedSection]:
    """Find the top resume chunks most relevant to the job description.

    Always returns exactly _TOP_K_SECTIONS results (even at moderate
    similarity) — similarity is a relative rank, not a hard gate.

    Algorithm:
        1. Chunk both texts.
        2. Batch-embed all chunks.
        3. Build a similarity matrix (resume_chunks × jd_chunks).
        4. For each resume chunk take its best JD-chunk similarity.
        5. Return the top-K resume chunks sorted by best similarity.
    """
    resume_chunks = split_into_chunks(resume_text)
    jd_chunks = split_into_chunks(job_description)

    if not resume_chunks:
        return []

    # If JD is a single short phrase after expansion it may still not chunk
    # properly — embed the full JD text as a single "chunk" fallback.
    if not jd_chunks:
        jd_chunks = [job_description]

    # Batch-embed (one model call per set of chunks)
    resume_embs = get_embeddings_batch(resume_chunks)   # (R, D)
    jd_embs     = get_embeddings_batch(jd_chunks)       # (J, D)

    # Similarity matrix via dot product (embeddings are already normalised)
    sim_matrix: np.ndarray = resume_embs @ jd_embs.T   # (R, J)

    # For each resume chunk, find the best-matching JD chunk
    best_jd_idx = sim_matrix.argmax(axis=1)             # (R,)
    best_sim    = sim_matrix.max(axis=1)                # (R,)

    # Rank resume chunks by similarity (descending); always take top-K
    k = min(_TOP_K_SECTIONS, len(resume_chunks))
    top_indices = best_sim.argsort()[::-1][:k]

    matched: list[MatchedSection] = []
    for idx in top_indices:
        matched.append(
            MatchedSection(
                resume_chunk=resume_chunks[idx],
                job_chunk=jd_chunks[int(best_jd_idx[idx])],
                similarity_score=round(float(best_sim[idx]), 4),
            )
        )

    return matched
