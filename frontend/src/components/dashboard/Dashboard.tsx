"use client";

import { AnalysisResponse } from "@/types/api";
import HeroScore from "./HeroScore";
import ScoreCards from "./ScoreCards";
import SkillsAnalysis from "./SkillsAnalysis";
import EvidenceExplorer from "./EvidenceExplorer";
import ProjectRelevance from "./ProjectRelevance";
import ATSChecklist from "./ATSChecklist";
import FeedbackCard from "./FeedbackCard";
import RecommendationList from "./RecommendationList";
import AnalyticsCharts from "./AnalyticsCharts";

interface DashboardProps {
  results: AnalysisResponse;
}

export default function Dashboard({ results }: DashboardProps) {
  return (
    <div className="w-full space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-12">
      
      {/* 1. Hero Score */}
      <HeroScore score={results.overall_score} />
      
      {/* 2. Score Cards Grid */}
      <ScoreCards results={results} />
      
      {/* 3. Analytics Charts */}
      <AnalyticsCharts results={results} />
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column - Skills & Evidence */}
        <div className="lg:col-span-2 space-y-8">
          <SkillsAnalysis results={results} />
          
          <EvidenceExplorer evidence={results.evidence} />
          
          <ProjectRelevance semanticMatches={results.semantic_matches} />
        </div>
        
        {/* Right Column - ATS, Feedback & Checklist */}
        <div className="lg:col-span-1 space-y-8">
          <FeedbackCard feedback={results.ai_feedback} />
          
          <ATSChecklist formatting={results.formatting} />
          
          <RecommendationList recommendations={results.recommendations} />
        </div>

      </div>
    </div>
  );
}
