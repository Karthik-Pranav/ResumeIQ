"""Job description parsing utility.

Extracts structured sections from a raw text job description.
"""

import re
from dataclasses import dataclass, field

@dataclass
class ParsedJD:
    title: str = ""
    responsibilities: list[str] = field(default_factory=list)
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    experience: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "responsibilities": self.responsibilities,
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "education": self.education,
            "experience": self.experience
        }

def parse_jd(text: str) -> ParsedJD:
    """Parse raw JD text into structured sections."""
    parsed = ParsedJD()
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        if len(lines[0]) < 80:
            parsed.title = lines[0]
            
    headers = {
        "responsibilities": r'^RESPONSIBILITIES|WHAT YOU WILL DO|WHAT YOU\'LL DO|YOUR ROLE',
        "required_skills": r'^REQUIREMENTS|REQUIRED SKILLS|QUALIFICATIONS|WHAT YOU NEED',
        "preferred_skills": r'^PREFERRED|NICE TO HAVE|BONUS SKILLS',
        "education": r'^EDUCATION',
        "experience": r'^EXPERIENCE'
    }
    
    current_section = None
    section_content = {k: [] for k in headers.keys()}
    
    for line in lines:
        upper_line = line.upper()
        matched_header = False
        
        for key, pattern in headers.items():
            if re.match(pattern + r'\s*:?$', upper_line):
                current_section = key
                matched_header = True
                break
                
        if not matched_header and current_section:
            section_content[current_section].append(line)
            
    def extract_bullets(lines_list: list[str]) -> list[str]:
        # Simple extraction of bullets or sentences
        items = []
        for line in lines_list:
            clean_line = re.sub(r'^[•\-\*]\s*', '', line).strip()
            if clean_line:
                items.append(clean_line)
        return items
        
    parsed.responsibilities = extract_bullets(section_content["responsibilities"])
    parsed.required_skills = extract_bullets(section_content["required_skills"])
    parsed.preferred_skills = extract_bullets(section_content["preferred_skills"])
    parsed.education = extract_bullets(section_content["education"])
    parsed.experience = extract_bullets(section_content["experience"])
    
    # Fallback: if no sections matched, dump everything into requirements
    if not any([parsed.responsibilities, parsed.required_skills, parsed.preferred_skills]):
        parsed.required_skills = extract_bullets(lines)
        
    return parsed
