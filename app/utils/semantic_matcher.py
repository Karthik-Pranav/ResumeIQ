"""Semantic matching logic.

Compares JD Responsibilities against Resume Experience/Projects using cosine similarity.
"""

from app.models.schemas import SemanticMatch
from app.utils.resume_parser import ParsedResume
from app.utils.jd_parser import ParsedJD
from app.utils.embedding import get_embeddings_batch
import numpy as np

def calculate_semantic_matches(parsed_resume: ParsedResume, parsed_jd: ParsedJD) -> list[SemanticMatch]:
    """Find semantic matches between JD responsibilities and Resume experience/projects."""
    
    # 1. Gather all resume blocks (Experience + Projects)
    resume_blocks = []
    if parsed_resume.experience:
        resume_blocks.extend(parsed_resume.experience)
    if parsed_resume.projects:
        resume_blocks.extend(parsed_resume.projects)
        
    if not resume_blocks or not parsed_jd.responsibilities:
        return []
        
    # 2. Get embeddings
    resume_embs = get_embeddings_batch(resume_blocks)
    jd_embs = get_embeddings_batch(parsed_jd.responsibilities)
    
    # 3. Calculate similarity matrix
    sim_matrix = resume_embs @ jd_embs.T
    
    matches: list[SemanticMatch] = []
    
    # For each JD responsibility, find the best matching resume block
    for j, jd_res in enumerate(parsed_jd.responsibilities):
        best_resume_idx = sim_matrix[:, j].argmax()
        best_sim = float(sim_matrix[best_resume_idx, j])
        
        # Only include if similarity is above a certain threshold (e.g., 0.5)
        if best_sim > 0.5:
            matches.append(SemanticMatch(
                resume_text=resume_blocks[best_resume_idx],
                jd_responsibility=jd_res,
                similarity_score=round(best_sim, 4)
            ))
            
    # Sort by highest similarity
    matches.sort(key=lambda x: x.similarity_score, reverse=True)
    return matches
