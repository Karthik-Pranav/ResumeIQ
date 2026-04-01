"""Keyword-based resume vs job-description analysis.

This module is the public API used by analysis_service.  It delegates to
three focused sub-modules introduced in the intelligence upgrade:

  jd_expander      — detects weak/vague JDs and expands them
  keyword_extractor — structured phrase extraction (core_skills/tools/concepts)
  semantic_matcher  — embedding-based skill presence detection

The KeywordResult dataclass is kept identical to the original so
analysis_service.py requires no import changes.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.utils.jd_expander import JDExpansionResult, expand_jd
from app.utils.keyword_extractor import ExtractedKeywords, extract_keywords
from app.utils.semantic_matcher import SemanticMatchResult, semantic_skill_match


@dataclass
class KeywordResult:
    """Outcome of keyword comparison between resume and job description."""

    strengths: list[str]
    gaps: list[str]
    # New optional fields — None when JD was not expanded
    jd_expansion: JDExpansionResult | None = None
    extracted_keywords: ExtractedKeywords | None = None


def analyze_keywords(
    resume_text: str,
    job_description: str,
    *,
    top_n: int = 6,
) -> KeywordResult:
    """Compare job-description keywords against resume text.

    Pipeline:
        1. Detect weak JD → expand with role-skill cluster if needed.
        2. Extract structured keywords (phrase whitelist + residual tokens).
        3. Semantic skill match via embeddings (cosine sim per skill).
        4. Return strengths / gaps + metadata for service layer.

    Args:
        resume_text:     Plain text from the candidate's resume.
        job_description: Raw job description input from the user.
        top_n:           Max strengths and gaps to return each.

    Returns:
        A KeywordResult containing strengths, gaps, and expansion metadata.
    """
    # Step 1 — expand if weak
    expansion: JDExpansionResult = expand_jd(job_description)

    # Step 2 — extract structured keywords from (possibly expanded) JD
    keywords: ExtractedKeywords = extract_keywords(expansion.expanded_jd)

    # Step 3 — semantic match
    all_skills = keywords.all_skills()
    match_result: SemanticMatchResult = semantic_skill_match(
        all_skills, resume_text, top_n=top_n
    )

    return KeywordResult(
        strengths=match_result.strengths,
        gaps=match_result.gaps,
        jd_expansion=expansion,
        extracted_keywords=keywords,
    )
