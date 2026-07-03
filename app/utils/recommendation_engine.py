"""Recommendation Engine.

Generates deterministic formatting suggestions and skill gap analysis based on the parsed results.
"""

from app.models.schemas import ATSFormattingScore

def generate_recommendations(
    formatting: ATSFormattingScore,
    missing_required: list[str],
    missing_preferred: list[str]
) -> list[str]:
    """Generate a list of actionable recommendations."""
    recs = []
    
    # Missing skills
    if missing_required:
        recs.append(f"Critical: Add missing required skills if you have experience with them: {', '.join(missing_required)}")
        
    if missing_preferred:
        recs.append(f"Consider adding preferred skills to boost your match: {', '.join(missing_preferred)}")
        
    # Formatting
    if not formatting.has_contact_details:
        recs.append("Add an email or phone number to your resume. Recruiters need a way to contact you.")
    if not formatting.has_linkedin:
        recs.append("Include a link to your LinkedIn profile.")
    if not formatting.has_github:
        recs.append("Include a link to your GitHub or portfolio to showcase your work.")
    if not formatting.has_professional_summary:
        recs.append("Add a Professional Summary at the top of your resume to quickly highlight your value proposition.")
    if not formatting.has_skills_section:
        recs.append("Create a dedicated 'Skills' section so ATS systems can easily parse your keywords.")
    if not formatting.has_education:
        recs.append("Add an Education section, even if you are self-taught or attended a bootcamp.")
    if not formatting.has_projects and not formatting.has_experience:
        recs.append("You are missing both Projects and Experience sections. Add your professional history or personal projects.")
        
    return recs
