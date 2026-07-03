"""ATS Scoring logic.

Replaces the single embedding score with a detailed weighted sum approach.
"""

from app.models.schemas import ATSFormattingScore, SemanticMatch
from app.utils.resume_parser import ParsedResume

# Scoring weights (must sum to 1.0)
WEIGHTS = {
    "required_skills": 0.40,
    "preferred_skills": 0.15,
    "projects": 0.15,
    "experience": 0.10,
    "education": 0.05,
    "formatting": 0.10,
    "semantic": 0.05
}

def analyze_formatting(parsed: ParsedResume) -> ATSFormattingScore:
    """Analyze the resume for basic ATS compatibility and formatting."""
    score = ATSFormattingScore()
    
    if parsed.email or parsed.phone:
        score.has_contact_details = True
    if parsed.github:
        score.has_github = True
    if parsed.linkedin:
        score.has_linkedin = True
    if parsed.about:
        score.has_professional_summary = True
    if parsed.skills:
        score.has_skills_section = True
    if parsed.education:
        score.has_education = True
    if parsed.projects:
        score.has_projects = True
    if parsed.experience:
        score.has_experience = True
        
    return score

def calculate_scores(
    matched_required: int,
    total_required: int,
    matched_preferred: int,
    total_preferred: int,
    parsed_resume: ParsedResume,
    semantic_matches: list[SemanticMatch],
    formatting: ATSFormattingScore
) -> dict[str, int]:
    """Calculate sub-scores and overall score based on the weighted formula."""
    
    # 1. Required Skills (40%)
    required_score = 100
    if total_required > 0:
        required_score = int((matched_required / total_required) * 100)
        
    # 2. Preferred Skills (15%)
    preferred_score = 100
    if total_preferred > 0:
        preferred_score = int((matched_preferred / total_preferred) * 100)
        
    # 3. Projects (15%)
    # Very basic heuristic: 100 if they have >= 2 projects, 50 if 1, 0 if none
    projects_score = 0
    if len(parsed_resume.projects) >= 2:
        projects_score = 100
    elif len(parsed_resume.projects) == 1:
        projects_score = 50
        
    # 4. Experience (10%)
    # 100 if >= 2 experience blocks
    experience_score = 0
    if len(parsed_resume.experience) >= 2:
        experience_score = 100
    elif len(parsed_resume.experience) == 1:
        experience_score = 60
        
    # 5. Education (5%)
    education_score = 100 if parsed_resume.education else 0
    
    # 6. Formatting (10%)
    # Simple ratio of the true boolean properties
    format_props = [
        formatting.has_contact_details,
        formatting.has_professional_summary,
        formatting.has_skills_section,
        formatting.has_education,
        formatting.has_experience
    ]
    formatting_score = int((sum(format_props) / len(format_props)) * 100)
    
    # 7. Semantic Score (5%)
    # Average semantic similarity of the matches (if none, then 50 if no requirements, else 0)
    semantic_score = 50
    if semantic_matches:
        avg_sim = sum(m.similarity_score for m in semantic_matches) / len(semantic_matches)
        semantic_score = int(avg_sim * 100)
    elif not total_required and not total_preferred:
        semantic_score = 100
        
    # 8. Overall Score
    overall = (
        (required_score * WEIGHTS["required_skills"]) +
        (preferred_score * WEIGHTS["preferred_skills"]) +
        (projects_score * WEIGHTS["projects"]) +
        (experience_score * WEIGHTS["experience"]) +
        (education_score * WEIGHTS["education"]) +
        (formatting_score * WEIGHTS["formatting"]) +
        (semantic_score * WEIGHTS["semantic"])
    )
    
    return {
        "required_skills_score": required_score,
        "preferred_skills_score": preferred_score,
        "projects_score": projects_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "ats_score": formatting_score,
        "semantic_score": semantic_score,
        "overall_score": int(overall)
    }
