"""Resume analysis service — business logic layer.

Orchestrates the v3 Pipeline:
1. Parse Resume -> Structured JSON
2. Parse JD -> Structured JSON
3. Keyword Matching (with Ontology and Normalization)
4. Semantic Matching
5. ATS Scoring
6. Recommendations & AI Feedback
"""

from __future__ import annotations

import asyncio
import logging

from app.models.schemas import AnalysisResponse
from app.utils.resume_parser import parse_resume
from app.utils.jd_parser import parse_jd
from app.utils.keyword_matcher import match_skills
from app.utils.semantic_matcher import calculate_semantic_matches
from app.utils.ats_scorer import analyze_formatting, calculate_scores
from app.utils.recommendation_engine import generate_recommendations
from app.utils.feedback_generator import generate_ai_feedback

logger = logging.getLogger(__name__)

async def analyze_resume(resume_text: str, job_description: str) -> AnalysisResponse:
    """Analyse a resume against a job description using the v3 modular pipeline.

    Args:
        resume_text:     Plain-text content extracted from the resume PDF.
        job_description: The target job description to compare against.

    Returns:
        An AnalysisResponse containing detailed scores, evidence, and AI feedback.
    """
    
    # 1. Parse texts into structured data
    parsed_resume = await asyncio.to_thread(parse_resume, resume_text)
    parsed_jd = await asyncio.to_thread(parse_jd, job_description)
    
    # 2. Keyword Matching (includes Normalization and Ontology internally)
    kw_results = await asyncio.to_thread(
        match_skills, 
        parsed_jd.required_skills, 
        parsed_jd.preferred_skills, 
        parsed_resume
    )
    
    matched_skills = kw_results["matched_skills"]
    missing_required = kw_results["missing_required"]
    missing_preferred = kw_results["missing_preferred"]
    evidence = kw_results["evidence"]
    
    # 3. Semantic Matching (Projects/Experience vs JD Responsibilities)
    semantic_matches = await asyncio.to_thread(
        calculate_semantic_matches,
        parsed_resume,
        parsed_jd
    )
    
    # 4. ATS Formatting Analysis
    formatting = await asyncio.to_thread(analyze_formatting, parsed_resume)
    
    # 5. Calculate Final Scores
    scores = await asyncio.to_thread(
        calculate_scores,
        matched_required=len([s for s in parsed_jd.required_skills if s in matched_skills]),
        total_required=len(parsed_jd.required_skills),
        matched_preferred=len([s for s in parsed_jd.preferred_skills if s in matched_skills]),
        total_preferred=len(parsed_jd.preferred_skills),
        parsed_resume=parsed_resume,
        semantic_matches=semantic_matches,
        formatting=formatting
    )
    
    # 6. Generate Recommendations
    recommendations = await asyncio.to_thread(
        generate_recommendations,
        formatting,
        missing_required,
        missing_preferred
    )
    
    # 7. Generate AI Feedback
    # Prepare dict for feedback generator
    feedback_payload = {
        "overall_score": scores["overall_score"],
        "matched_skills": matched_skills,
        "missing_required": missing_required,
        "missing_preferred": missing_preferred,
        "recommendations": recommendations
    }
    
    ai_feedback = await asyncio.to_thread(generate_ai_feedback, feedback_payload)
    
    # 8. Return response conforming to new AnalysisResponse schema
    return AnalysisResponse(
        overall_score=scores["overall_score"],
        required_skills_score=scores["required_skills_score"],
        preferred_skills_score=scores["preferred_skills_score"],
        semantic_score=scores["semantic_score"],
        ats_score=scores["ats_score"],
        experience_score=scores["experience_score"],
        education_score=scores["education_score"],
        projects_score=scores["projects_score"],
        
        matched_skills=matched_skills,
        missing_required=missing_required,
        missing_preferred=missing_preferred,
        
        evidence=evidence,
        semantic_matches=semantic_matches,
        
        formatting=formatting,
        recommendations=recommendations,
        ai_feedback=ai_feedback
    )
