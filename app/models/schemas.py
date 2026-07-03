"""Pydantic models for the resume analysis API."""

from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field


class MatchedSection(BaseModel):
    """A resume chunk matched against a job-description chunk."""
    resume_chunk: str = Field(..., description="Text segment from the resume.")
    job_chunk: str = Field(..., description="Most relevant job-description segment.")
    similarity_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="Cosine similarity between the two chunks (0.0–1.0).",
    )


class SkillEvidence(BaseModel):
    """Evidence showing where a skill was found and the confidence level."""
    confidence: str = Field(..., description="Confidence level (e.g., 'High', 'Medium', 'Low')")
    found_in: list[str] = Field(default_factory=list, description="Sections or projects where this was found.")


class SemanticMatch(BaseModel):
    """Semantic match between a resume project/experience and a JD responsibility."""
    resume_text: str = Field(..., description="The project or experience text from the resume.")
    jd_responsibility: str = Field(..., description="The matched job responsibility.")
    similarity_score: float = Field(..., description="Cosine similarity score.")


class ATSFormattingScore(BaseModel):
    """Detailed formatting checks."""
    has_contact_details: bool = False
    has_github: bool = False
    has_linkedin: bool = False
    has_professional_summary: bool = False
    has_skills_section: bool = False
    has_education: bool = False
    has_projects: bool = False
    has_experience: bool = False
    readable_headings: bool = True
    parse_quality_good: bool = True
    resume_length_optimal: bool = True
    section_ordering_logical: bool = True


class AnalysisResponse(BaseModel):
    """Response model returned by the /analyze endpoint (v3 Architecture)."""
    
    # ── Scores ──
    overall_score: int = Field(..., ge=0, le=100)
    required_skills_score: int = Field(..., ge=0, le=100)
    preferred_skills_score: int = Field(..., ge=0, le=100)
    semantic_score: int = Field(..., ge=0, le=100)
    ats_score: int = Field(..., ge=0, le=100)
    experience_score: int = Field(..., ge=0, le=100)
    education_score: int = Field(..., ge=0, le=100)
    projects_score: int = Field(..., ge=0, le=100)

    # ── Skills ──
    matched_skills: list[str] = Field(default_factory=list)
    missing_required: list[str] = Field(default_factory=list)
    missing_preferred: list[str] = Field(default_factory=list)
    
    # ── Detailed Evidence ──
    evidence: dict[str, SkillEvidence] = Field(
        default_factory=dict, 
        description="Mapping of skill names to their evidence."
    )
    semantic_matches: list[SemanticMatch] = Field(default_factory=list)
    
    # ── ATS & Feedback ──
    formatting: ATSFormattingScore = Field(default_factory=ATSFormattingScore)
    recommendations: list[str] = Field(default_factory=list)
    ai_feedback: str = Field(
        "", 
        description="Detailed LLM-generated feedback explaining matches and suggesting improvements."
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "overall_score": 91,
                    "required_skills_score": 95,
                    "preferred_skills_score": 68,
                    "semantic_score": 90,
                    "ats_score": 94,
                    "experience_score": 85,
                    "education_score": 100,
                    "projects_score": 96,
                    "matched_skills": ["Python", "Machine Learning", "FastAPI"],
                    "missing_required": ["Kubernetes"],
                    "missing_preferred": ["GraphQL"],
                    "evidence": {
                        "Python": {
                            "confidence": "High",
                            "found_in": ["Technical Skills", "Resume Analyzer Project"]
                        }
                    },
                    "semantic_matches": [],
                    "formatting": {
                        "has_contact_details": True,
                        "has_github": True,
                        "has_linkedin": True,
                        "has_professional_summary": True,
                        "has_skills_section": True,
                        "has_education": True,
                        "has_projects": True,
                        "has_experience": True,
                        "readable_headings": True,
                        "parse_quality_good": True,
                        "resume_length_optimal": True,
                        "section_ordering_logical": True
                    },
                    "recommendations": ["Add Kubernetes to your skills section if you have experience with it."],
                    "ai_feedback": "Your resume is a strong match for this role, particularly your Python and ML experience."
                }
            ]
        }
    }

