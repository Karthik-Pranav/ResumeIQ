"""Skill Ontology Layer.

Maps skills to their inferred dependencies/parents.
Example: 'FastAPI' implies 'Python' and 'REST API'.
"""

# Dictionary mapping a canonical skill to a list of inferred canonical skills
ONTOLOGY = {
    "fastapi": ["python", "rest api", "backend"],
    "django": ["python", "backend", "web development"],
    "flask": ["python", "rest api", "backend"],
    "next.js": ["react", "javascript", "typescript", "frontend", "ssr"],
    "react": ["javascript", "frontend", "ui"],
    "express.js": ["node.js", "javascript", "backend", "rest api"],
    "node.js": ["javascript", "backend"],
    "spring boot": ["java", "backend", "rest api"],
    "rag": ["embeddings", "vector database", "large language models", "semantic search"],
    "pandas": ["python", "data analysis"],
    "numpy": ["python", "data analysis"],
    "kubernetes": ["docker", "containerization", "devops", "cloud"],
    "tensorflow": ["machine learning", "python", "deep learning"],
    "pytorch": ["machine learning", "python", "deep learning"],
}

def get_inferred_skills(skill: str) -> list[str]:
    """Return a list of inferred skills for a given canonical skill."""
    return ONTOLOGY.get(skill, [])

def expand_skills(skills: list[str]) -> set[str]:
    """Expand a list of canonical skills to include inferred skills."""
    expanded = set(skills)
    for skill in skills:
        inferred = get_inferred_skills(skill)
        expanded.update(inferred)
    return expanded
