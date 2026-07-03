import { AnalysisResponse } from "@/types/api";

interface HeroScoreProps {
  score: number;
}

export default function HeroScore({ score }: HeroScoreProps) {
  let title = "";
  let message = "";
  let color = "";

  if (score >= 80) {
    title = "Excellent Match";
    message = "Your resume strongly matches this role. Improving minor missing skills could further increase recruiter confidence.";
    color = "text-green-500";
  } else if (score >= 60) {
    title = "Good Match";
    message = "Your resume is a good fit, but you are missing some key requirements. Consider tailoring your experience section.";
    color = "text-blue-500";
  } else if (score >= 40) {
    title = "Fair Match";
    message = "Your resume has some overlap, but is missing major requirements. Significant tailoring is recommended.";
    color = "text-orange-500";
  } else {
    title = "Needs Improvement";
    message = "Your resume is currently a weak match for this role. Review the missing required skills and consider gaining experience in these areas.";
    color = "text-red-500";
  }

  // Calculate SVG stroke dasharray for the circular progress
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col md:flex-row items-center bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-8 gap-8">
      
      {/* Circular Progress Indicator */}
      <div className="relative flex items-center justify-center shrink-0">
        <svg className="w-40 h-40 transform -rotate-90">
          {/* Background circle */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            className="stroke-gray-100 dark:stroke-gray-700"
            strokeWidth="12"
            fill="none"
          />
          {/* Progress circle */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            className={`stroke-current ${color} transition-all duration-1000 ease-out`}
            strokeWidth="12"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center">
          <span className="text-4xl font-bold text-gray-900 dark:text-white">
            {score}%
          </span>
          <span className="text-xs font-medium text-gray-500 uppercase tracking-wide mt-1">
            Match
          </span>
        </div>
      </div>

      {/* Summary Text */}
      <div className="flex flex-col space-y-3 text-center md:text-left">
        <h2 className={`text-2xl font-bold ${color}`}>
          {title}
        </h2>
        <p className="text-gray-600 dark:text-gray-300 text-lg leading-relaxed max-w-xl">
          {message}
        </p>
      </div>
      
    </div>
  );
}
