"""Pydantic models for the resume analysis API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MatchedSection(BaseModel):
    """A resume chunk matched against a job-description chunk."""

    resume_chunk: str = Field(..., description="Text segment from the resume.")
    job_chunk: str = Field(..., description="Most relevant job-description segment.")
    similarity_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="Cosine similarity between the two chunks (0.0–1.0).",
    )


class AnalysisResponse(BaseModel):
    """Response model returned by the /analyze endpoint."""

    match_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="How well the resume matches the job description (0-100).",
    )
    strengths: list[str] = Field(
        ...,
        description="Semantically matched skills found in the resume.",
    )
    gaps: list[str] = Field(
        ...,
        description="Skills required by the JD but not found in the resume.",
    )
    matched_sections: list[MatchedSection] = Field(
        ...,
        description="Top resume chunks most relevant to the job description.",
    )
    # ── Intelligence upgrade v2 fields (all optional / backward-compatible) ──
    jd_warning: str | None = Field(
        None,
        description=(
            "Present when the job description was short or vague. "
            "Explains how it was expanded before analysis."
        ),
    )
    matched_role: str | None = Field(
        None,
        description="Canonical role name matched during JD expansion, if any.",
    )
    keyword_breakdown: dict[str, list[str]] | None = Field(
        None,
        description=(
            "Structured keyword breakdown: "
            "{'core_skills': [...], 'tools': [...], 'concepts': [...]}."
        ),
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "match_score": 72,
                    "strengths": [
                        "Machine Learning — strong match (score: 0.81)",
                        "Python — strong match (score: 0.78)",
                    ],
                    "gaps": ["kubernetes", "model deployment"],
                    "matched_sections": [
                        {
                            "resume_chunk": "5 years building REST APIs with FastAPI",
                            "job_chunk": "Experience with Python and REST API design",
                            "similarity_score": 0.82,
                        }
                    ],
                    "jd_warning": (
                        "Short job description detected. "
                        "Automatically expanded using the 'ai developer' role profile "
                        "(8 skills added)."
                    ),
                    "matched_role": "ai developer",
                    "keyword_breakdown": {
                        "core_skills": ["machine learning", "deep learning", "python"],
                        "tools": ["tensorflow", "pytorch"],
                        "concepts": ["model deployment", "nlp"],
                    },
                }
            ]
        }
    }
