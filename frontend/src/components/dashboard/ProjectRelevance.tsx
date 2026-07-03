import { FolderGit2 } from "lucide-react";
import { SemanticMatch } from "@/types/api";

interface ProjectRelevanceProps {
  semanticMatches: SemanticMatch[];
}

export default function ProjectRelevance({ semanticMatches }: ProjectRelevanceProps) {
  if (!semanticMatches || semanticMatches.length === 0) {
    return null;
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-6 md:p-8 space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-lg">
          <FolderGit2 className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Semantic Match Alignment
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            How well your experience logically aligns with the job responsibilities.
          </p>
        </div>
      </div>

      <div className="space-y-6">
        {semanticMatches.map((match, idx) => {
          // Cap similarity score visually at 100%
          const percent = Math.min(Math.round(match.similarity_score * 100), 100);
          
          let color = "bg-blue-500";
          if (percent >= 80) color = "bg-green-500";
          else if (percent < 50) color = "bg-orange-500";

          return (
            <div key={idx} className="bg-gray-50 dark:bg-gray-900/50 rounded-xl p-5 border border-gray-100 dark:border-gray-800">
              
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Responsibility Match
                </span>
                <span className="text-lg font-bold text-gray-900 dark:text-white">
                  {percent}%
                </span>
              </div>

              {/* Progress Bar */}
              <div className="h-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden mb-4">
                <div 
                  className={`h-full ${color} rounded-full transition-all duration-1000 ease-out`}
                  style={{ width: `${percent}%` }}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100 mb-1">Job Description:</p>
                  <p className="text-gray-600 dark:text-gray-400 line-clamp-3">"{match.jd_responsibility}"</p>
                </div>
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100 mb-1">Your Resume:</p>
                  <p className="text-gray-600 dark:text-gray-400 line-clamp-3">"{match.resume_text}"</p>
                </div>
              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
}
