"""Keyword matching logic.

Matches normalized skills from the JD against the parsed Resume JSON sections.
Generates evidence mapping showing where skills were found.
"""

from app.utils.skill_normalizer import normalize_skill
from app.utils.skill_ontology import expand_skills
from app.models.schemas import SkillEvidence
from app.utils.resume_parser import ParsedResume

def match_skills(
    jd_required_skills: list[str], 
    jd_preferred_skills: list[str], 
    parsed_resume: ParsedResume
) -> dict:
    """Matches JD skills against the resume and generates evidence.
    
    Returns a dictionary containing:
        - matched_skills: list[str]
        - missing_required: list[str]
        - missing_preferred: list[str]
        - evidence: dict[str, SkillEvidence]
    """
    
    # 1. Normalize JD skills
    required_norm = {normalize_skill(s): s for s in jd_required_skills if s.strip()}
    preferred_norm = {normalize_skill(s): s for s in jd_preferred_skills if s.strip()}
    
    # 2. Extract and normalize all skills from Resume sections
    resume_sections = {
        "Skills": parsed_resume.skills,
        "Experience": parsed_resume.experience,
        "Projects": parsed_resume.projects,
        "Education": parsed_resume.education,
        "About": [parsed_resume.about] if parsed_resume.about else []
    }
    
    # Create an inverted index of normalized resume words/phrases to sections
    # This is a heuristic approach: we check if the normalized JD skill exists in the section text
    evidence_map: dict[str, set[str]] = {}
    
    for section_name, blocks in resume_sections.items():
        text_content = " ".join(blocks).lower()
        
        for norm_skill in list(required_norm.keys()) + list(preferred_norm.keys()):
            # Exact substring match for the normalized skill
            if norm_skill in text_content:
                if norm_skill not in evidence_map:
                    evidence_map[norm_skill] = set()
                evidence_map[norm_skill].add(section_name)
    
    # 3. Apply ontology (If they have FastAPI, they have Python)
    # Check if we found exact matches
    found_norm_skills = set(evidence_map.keys())
    
    # What did we find from ontology expansion of found skills?
    expanded_found = expand_skills(list(found_norm_skills))
    
    # If a JD skill is in expanded_found, but not directly found, we mark it as inferred
    for norm_skill in list(required_norm.keys()) + list(preferred_norm.keys()):
        if norm_skill not in found_norm_skills and norm_skill in expanded_found:
            evidence_map[norm_skill] = set(["Inferred from other skills"])
            
    # 4. Compile results
    matched_skills = []
    missing_required = []
    missing_preferred = []
    evidence_output: dict[str, SkillEvidence] = {}
    
    # Process required
    for norm_skill, original_skill in required_norm.items():
        if norm_skill in evidence_map:
            matched_skills.append(original_skill)
            
            # Determine confidence
            found_in = list(evidence_map[norm_skill])
            confidence = "High"
            if "Inferred from other skills" in found_in:
                confidence = "Medium"
            elif "Skills" not in found_in and "Experience" not in found_in:
                confidence = "Low"
                
            evidence_output[original_skill] = SkillEvidence(
                confidence=confidence,
                found_in=found_in
            )
        else:
            missing_required.append(original_skill)
            
    # Process preferred
    for norm_skill, original_skill in preferred_norm.items():
        if norm_skill in evidence_map:
            matched_skills.append(original_skill)
            
            found_in = list(evidence_map[norm_skill])
            confidence = "High"
            if "Inferred from other skills" in found_in:
                confidence = "Medium"
            elif "Skills" not in found_in and "Experience" not in found_in:
                confidence = "Low"
                
            evidence_output[original_skill] = SkillEvidence(
                confidence=confidence,
                found_in=found_in
            )
        else:
            missing_preferred.append(original_skill)
            
    return {
        "matched_skills": matched_skills,
        "missing_required": missing_required,
        "missing_preferred": missing_preferred,
        "evidence": evidence_output
    }
