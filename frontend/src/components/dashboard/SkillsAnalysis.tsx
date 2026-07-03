import { useState } from "react";
import { Check, X, AlertCircle } from "lucide-react";
import { AnalysisResponse } from "@/types/api";
import { motion, AnimatePresence } from "framer-motion";

interface SkillsAnalysisProps {
  results: AnalysisResponse;
}

export default function SkillsAnalysis({ results }: SkillsAnalysisProps) {
  const [hoveredSkill, setHoveredSkill] = useState<string | null>(null);

  const matchedSkills = results.matched_skills || [];
  const missingRequired = results.missing_required || [];
  const missingPreferred = results.missing_preferred || [];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-6 md:p-8 space-y-8">
      
      <div>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Skills Match Analysis
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
          Hover over any skill to see how it impacted your ATS scan.
        </p>
      </div>

      <div className="space-y-6">
        {/* Matched Skills */}
        {matchedSkills.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
              <Check className="w-4 h-4 text-green-500 mr-2" />
              Matched Skills
            </h3>
            <div className="flex flex-wrap gap-2 relative">
              {matchedSkills.map((skill) => (
                <SkillChip 
                  key={`matched-${skill}`} 
                  skill={skill} 
                  type="matched" 
                  evidence={results.evidence[skill]} 
                  isHovered={hoveredSkill === skill}
                  setHovered={setHoveredSkill}
                />
              ))}
            </div>
          </div>
        )}

        {/* Missing Required */}
        {missingRequired.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
              <X className="w-4 h-4 text-red-500 mr-2" />
              Missing Required Skills
            </h3>
            <div className="flex flex-wrap gap-2 relative">
              {missingRequired.map((skill) => (
                <SkillChip 
                  key={`missing-req-${skill}`} 
                  skill={skill} 
                  type="missing-required" 
                  isHovered={hoveredSkill === skill}
                  setHovered={setHoveredSkill}
                />
              ))}
            </div>
          </div>
        )}

        {/* Missing Preferred */}
        {missingPreferred.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
              <AlertCircle className="w-4 h-4 text-orange-500 mr-2" />
              Missing Preferred Skills
            </h3>
            <div className="flex flex-wrap gap-2 relative">
              {missingPreferred.map((skill) => (
                <SkillChip 
                  key={`missing-pref-${skill}`} 
                  skill={skill} 
                  type="missing-preferred" 
                  isHovered={hoveredSkill === skill}
                  setHovered={setHoveredSkill}
                />
              ))}
            </div>
          </div>
        )}
      </div>

    </div>
  );
}

interface SkillChipProps {
  skill: string;
  type: "matched" | "missing-required" | "missing-preferred";
  evidence?: { confidence: string; found_in: string[] };
  isHovered: boolean;
  setHovered: (s: string | null) => void;
}

function SkillChip({ skill, type, evidence, isHovered, setHovered }: SkillChipProps) {
  let baseClasses = "px-3 py-1.5 rounded-md text-sm font-medium border transition-colors cursor-help ";
  
  if (type === "matched") {
    baseClasses += "bg-green-50 text-green-700 border-green-200 hover:bg-green-100 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800";
  } else if (type === "missing-required") {
    baseClasses += "bg-red-50 text-red-700 border-red-200 hover:bg-red-100 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800";
  } else {
    baseClasses += "bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100 dark:bg-orange-900/30 dark:text-orange-400 dark:border-orange-800";
  }

  return (
    <div 
      className="relative"
      onMouseEnter={() => setHovered(skill)}
      onMouseLeave={() => setHovered(null)}
    >
      <span className={baseClasses}>
        {skill}
      </span>

      <AnimatePresence>
        {isHovered && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 5 }}
            className="absolute z-10 bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-xl pointer-events-none"
          >
            <div className="font-semibold mb-1">{skill}</div>
            
            {type === "matched" && evidence ? (
              <>
                <div className="text-gray-300">Confidence: <span className="text-white font-medium">{evidence.confidence}</span></div>
                <div className="text-gray-400 mt-1">Found in:</div>
                <ul className="list-disc list-inside text-gray-300 mt-0.5">
                  {evidence.found_in.map(sec => <li key={sec}>{sec}</li>)}
                </ul>
              </>
            ) : type === "missing-required" ? (
              <span className="text-gray-300">This skill is strictly required for the role but was not found in your resume.</span>
            ) : (
              <span className="text-gray-300">This is a nice-to-have skill. Adding it could boost your ranking.</span>
            )}
            
            <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
