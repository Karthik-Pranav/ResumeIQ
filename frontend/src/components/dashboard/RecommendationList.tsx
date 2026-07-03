import { Target, ArrowUpRight } from "lucide-react";

interface RecommendationListProps {
  recommendations: string[];
}

export default function RecommendationList({ recommendations }: RecommendationListProps) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-6 md:p-8 space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-lg">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Actionable Recommendations
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No major recommendations! Your resume is looking great.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-6 md:p-8 space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-pink-50 dark:bg-pink-900/30 text-pink-600 dark:text-pink-400 rounded-lg">
          <Target className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Actionable Recommendations
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Step-by-step tasks to improve your ATS score.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {recommendations.map((rec, idx) => {
          // A bit of heuristic to guess priority for styling
          let priority = "Medium Priority";
          let color = "text-yellow-600 bg-yellow-50 dark:text-yellow-400 dark:bg-yellow-900/20";
          let border = "border-yellow-200 dark:border-yellow-800";
          
          if (rec.toLowerCase().includes("critical") || rec.toLowerCase().includes("missing required")) {
            priority = "High Impact";
            color = "text-red-600 bg-red-50 dark:text-red-400 dark:bg-red-900/20";
            border = "border-red-200 dark:border-red-800";
          } else if (rec.toLowerCase().includes("consider") || rec.toLowerCase().includes("nice")) {
            priority = "Low Impact";
            color = "text-blue-600 bg-blue-50 dark:text-blue-400 dark:bg-blue-900/20";
            border = "border-blue-200 dark:border-blue-800";
          }

          return (
            <div key={idx} className={`relative p-5 rounded-xl border ${border} transition-colors hover:bg-gray-50 dark:hover:bg-gray-900/50`}>
              <div className="flex justify-between items-start gap-4">
                <div>
                  <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold mb-3 ${color}`}>
                    {priority}
                  </span>
                  <p className="text-gray-900 dark:text-gray-100 font-medium">
                    {rec.replace(/Critical:\s*/i, "")}
                  </p>
                </div>
                
                <button className="shrink-0 p-2 text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors" title="How to do this">
                  <ArrowUpRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
