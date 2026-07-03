"""Resume parsing utility.

Extracts structured sections from a raw text resume.
"""

import re
from dataclasses import dataclass, field

@dataclass
class ParsedResume:
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    about: str = ""
    skills: list[str] = field(default_factory=list)
    experience: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "linkedin": self.linkedin,
            "github": self.github,
            "about": self.about,
            "skills": self.skills,
            "experience": self.experience,
            "projects": self.projects,
            "education": self.education,
            "certifications": self.certifications
        }

def parse_resume(text: str) -> ParsedResume:
    """Parse raw resume text into structured sections."""
    parsed = ParsedResume()
    
    # 1. Extract contact info using regex
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    if email_match:
        parsed.email = email_match.group(0)
        
    phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    if phone_match:
        parsed.phone = phone_match.group(0)
        
    linkedin_match = re.search(r'(?:linkedin\.com/in/|linkedin:)[A-Za-z0-9_-]+', text, re.IGNORECASE)
    if linkedin_match:
        parsed.linkedin = linkedin_match.group(0)
        
    github_match = re.search(r'(?:github\.com/|github:)[A-Za-z0-9_-]+', text, re.IGNORECASE)
    if github_match:
        parsed.github = github_match.group(0)
        
    # 2. Extract Name (Heuristic: First non-empty line)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        # Avoid long lines for name
        if len(lines[0]) < 50:
            parsed.name = lines[0]
            
    # 3. Section splitting
    # Common headers in resumes
    headers = {
        "experience": r'^(?:WORK\s+)?EXPERIENCE|EMPLOYMENT|HISTORY',
        "education": r'^EDUCATION|ACADEMICS',
        "skills": r'^(?:TECHNICAL\s+)?SKILLS|TECHNOLOGIES',
        "projects": r'^PROJECTS|PERSONAL PROJECTS',
        "certifications": r'^CERTIFICATIONS|LICENSES',
        "about": r'^SUMMARY|ABOUT|OBJECTIVE|PROFILE'
    }
    
    current_section = None
    section_content = {k: [] for k in headers.keys()}
    
    for line in lines:
        upper_line = line.upper()
        matched_header = False
        
        for key, pattern in headers.items():
            # Strict header matching (full word, maybe with colons)
            if re.match(pattern + r'\s*:?$', upper_line):
                current_section = key
                matched_header = True
                break
                
        if not matched_header and current_section:
            section_content[current_section].append(line)
            
    # Process extracted content
    if section_content["skills"]:
        # Split by comma or newlines
        skills_text = " ".join(section_content["skills"])
        # Split into chunks of potential skills
        potential_skills = [s.strip() for s in re.split(r'[,|•]', skills_text) if s.strip()]
        if potential_skills:
            parsed.skills = potential_skills
        else:
            # Fallback to lines
            parsed.skills = section_content["skills"]
            
    # For others, we join by newline to preserve chunks, then split by bullet points if necessary.
    def extract_blocks(lines_list: list[str]) -> list[str]:
        text_block = "\n".join(lines_list)
        # Split by double newlines
        blocks = re.split(r'\n\s*\n', text_block)
        return [b.strip() for b in blocks if b.strip()]
        
    parsed.experience = extract_blocks(section_content["experience"])
    parsed.education = extract_blocks(section_content["education"])
    parsed.projects = extract_blocks(section_content["projects"])
    parsed.certifications = extract_blocks(section_content["certifications"])
    parsed.about = "\n".join(section_content["about"])
    
    # Fallback: if no sections matched, dump everything into experience for semantic matching fallback
    if not any([parsed.experience, parsed.education, parsed.skills, parsed.projects]):
        parsed.experience = extract_blocks(lines)
        
    return parsed
