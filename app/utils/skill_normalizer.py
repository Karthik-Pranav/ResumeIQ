"""Skill Normalization Layer.

Normalizes raw skill strings into a canonical format (e.g., lowercase, removing punctuation, standardizing acronyms).
Provides an alias mapping to easily expand the dictionary.
"""

import re

# Canonical skill mappings
SKILL_ALIASES = {
    # JavaScript
    "js": "javascript",
    "javascript": "javascript",
    "java script": "javascript",
    
    # React
    "react": "react",
    "react.js": "react",
    "reactjs": "react",
    
    # Node
    "node": "node.js",
    "node.js": "node.js",
    "nodejs": "node.js",
    
    # Databases
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "sql server": "microsoft sql server",
    "mssql": "microsoft sql server",
    "mongo": "mongodb",
    "mongodb": "mongodb",
    
    # Web / API
    "rest": "rest api",
    "rest api": "rest api",
    "rest apis": "rest api",
    "restful api": "rest api",
    "restful apis": "rest api",
    
    # Typescript
    "ts": "typescript",
    "typescript": "typescript",
    
    # Python
    "python": "python",
    "python3": "python",
    
    # AWS
    "aws": "aws",
    "amazon web services": "aws",
    
    # GCP
    "gcp": "gcp",
    "google cloud platform": "gcp",
    "google cloud": "gcp",
    
    # Azure
    "azure": "azure",
    "microsoft azure": "azure",
}

def normalize_skill(skill: str) -> str:
    """Normalize a skill string to its canonical form."""
    # Lowercase and strip whitespace
    cleaned = skill.lower().strip()
    # Remove trailing punctuation (like commas or periods at the end)
    cleaned = re.sub(r'[.,;!]+$', '', cleaned)
    
    # Check if exact match in aliases
    if cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[cleaned]
        
    return cleaned

def extract_and_normalize_skills(text_blocks: list[str]) -> list[str]:
    """Extract skills from text blocks using regex and normalize them.
    A very simple heuristic to get single/double word phrases.
    """
    text = " ".join(text_blocks)
    # Simple regex to split by commas or bullets
    raw_skills = [s.strip() for s in re.split(r'[,|•\n]', text) if s.strip()]
    
    normalized = set()
    for rs in raw_skills:
        if len(rs) > 1 and len(rs) < 50:
            normalized.add(normalize_skill(rs))
            
    return list(normalized)
