export interface MatchedSection {
  resume_chunk: string;
  job_chunk: string;
  similarity_score: number;
}

export interface SkillEvidence {
  confidence: string;
  found_in: string[];
}

export interface SemanticMatch {
  resume_text: string;
  jd_responsibility: string;
  similarity_score: number;
}

export interface ATSFormattingScore {
  has_contact_details: boolean;
  has_github: boolean;
  has_linkedin: boolean;
  has_professional_summary: boolean;
  has_skills_section: boolean;
  has_education: boolean;
  has_projects: boolean;
  has_experience: boolean;
  readable_headings: boolean;
  parse_quality_good: boolean;
  resume_length_optimal: boolean;
  section_ordering_logical: boolean;
}

export interface AnalysisResponse {
  // Scores
  overall_score: number;
  required_skills_score: number;
  preferred_skills_score: number;
  semantic_score: number;
  ats_score: number;
  experience_score: number;
  education_score: number;
  projects_score: number;

  // Skills
  matched_skills: string[];
  missing_required: string[];
  missing_preferred: string[];

  // Detailed Evidence
  evidence: Record<string, SkillEvidence>;
  semantic_matches: SemanticMatch[];

  // ATS & Feedback
  formatting: ATSFormattingScore;
  recommendations: string[];
  ai_feedback: string;
}
