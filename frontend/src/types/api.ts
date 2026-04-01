export interface MatchedSection {
  resume_chunk: string;
  job_chunk: string;
  similarity_score: number;
}

export interface KeywordBreakdown {
  core_skills: string[];
  tools: string[];
  concepts: string[];
}

export interface AnalysisResponse {
  match_score: number;
  strengths: string[];
  gaps: string[];
  matched_sections: MatchedSection[];
  // Intelligence upgrade v2 — optional fields
  jd_warning?: string | null;
  matched_role?: string | null;
  keyword_breakdown?: KeywordBreakdown | null;
}
