import { useState } from "react";
import { ChevronDown, ChevronRight, Fingerprint } from "lucide-react";
import { AnalysisResponse, SkillEvidence } from "@/types/api";
import { motion, AnimatePresence } from "framer-motion";

interface EvidenceExplorerProps {
  evidence: Record<string, SkillEvidence>;
}

export default function EvidenceExplorer({ evidence }: EvidenceExplorerProps) {
  const [expandedSkill, setExpandedSkill] = useState<string | null>(null);

  const entries = Object.entries(evidence);

  if (entries.length === 0) {
    return null;
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-6 md:p-8 space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg">
          <Fingerprint className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Evidence Explorer
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            See exactly where the ATS found your skills.
          </p>
        </div>
      </div>

      <div className="border border-gray-100 dark:border-gray-700 rounded-xl overflow-hidden divide-y divide-gray-100 dark:divide-gray-700">
        {entries.map(([skill, ev]) => {
          const isExpanded = expandedSkill === skill;
          
          return (
            <div key={skill} className="bg-white dark:bg-gray-800">
              <button
                onClick={() => setExpandedSkill(isExpanded ? null : skill)}
                className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-900/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-gray-400" />
                  )}
                  <span className="font-semibold text-gray-900 dark:text-gray-100">{skill}</span>
                </div>
                
                <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${
                  ev.confidence === "High" 
                    ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                    : ev.confidence === "Medium"
                    ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                    : "bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300"
                }`}>
                  {ev.confidence} Confidence
                </span>
              </button>

              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden bg-gray-50 dark:bg-gray-900/20"
                  >
                    <div className="p-4 pl-11 text-sm text-gray-600 dark:text-gray-300">
                      <p className="mb-2 font-medium text-gray-900 dark:text-gray-200">Found in:</p>
                      <ul className="list-disc list-inside space-y-1">
                        {ev.found_in.map((location, idx) => (
                          <li key={idx} className="marker:text-blue-500">{location}</li>
                        ))}
                      </ul>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </div>
  );
}
