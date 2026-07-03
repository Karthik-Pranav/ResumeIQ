"""AI Feedback Generator.

Interfaces with an LLM (e.g., OpenAI) to generate contextual feedback 
based solely on the structured JSON pipeline output.
"""

import os
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

def generate_ai_feedback(analysis_data: dict[str, Any]) -> str:
    """Generate AI feedback using an LLM.
    
    If the OPENAI_API_KEY is not set or the package is not installed,
    it falls back to a deterministic summary.
    """
    
    # 1. Fallback generation if no LLM is configured
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not found. Using fallback AI feedback.")
        return _generate_fallback_feedback(analysis_data)
        
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # Prepare the prompt
        system_prompt = (
            "You are an expert technical recruiter and ATS specialist. "
            "Your task is to provide personalized, concise, and constructive feedback "
            "to a candidate based on their ATS scan results. "
            "Do NOT invent any experience. Be encouraging but direct. "
            "Keep the feedback to 2-3 short paragraphs."
        )
        
        # We only send the essential structured JSON to save tokens and prevent hallucination
        safe_data = {
            "overall_score": analysis_data.get("overall_score"),
            "matched_skills": analysis_data.get("matched_skills"),
            "missing_required_skills": analysis_data.get("missing_required"),
            "missing_preferred_skills": analysis_data.get("missing_preferred"),
            "recommendations": analysis_data.get("recommendations")
        }
        
        user_prompt = f"Please analyze these ATS results and provide feedback:\n\n{json.dumps(safe_data, indent=2)}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=250,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Failed to generate AI feedback: {e}")
        return _generate_fallback_feedback(analysis_data)

def _generate_fallback_feedback(data: dict[str, Any]) -> str:
    """Generate a simple string based on the score when LLM is unavailable."""
    score = data.get("overall_score", 0)
    
    if score >= 80:
        return "Your resume is a strong match for this role! You have hit most of the required skills and your formatting is ATS-friendly. Make sure to prepare your portfolio and GitHub links for the interview."
    elif score >= 50:
        return "Your resume has moderate potential for this role. You are missing some required skills, which might lower your chances of passing an automated ATS filter. Try to incorporate the missing skills into your experience if you possess them."
    else:
        return "Your resume is currently a weak match for this role. It appears you are missing several core requirements. Please review the recommendations to improve your ATS formatting and ensure you are tailoring your resume to the specific job description."
