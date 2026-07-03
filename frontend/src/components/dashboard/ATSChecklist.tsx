import { Check, X, FileSearch } from "lucide-react";
import { ATSFormattingScore } from "@/types/api";

interface ATSChecklistProps {
  formatting: ATSFormattingScore;
}

export default function ATSChecklist({ formatting }: ATSChecklistProps) {
  const checks = [
    { key: "has_contact_details", label: "Contact Information (Email/Phone)" },
    { key: "has_linkedin", label: "LinkedIn Profile" },
    { key: "has_github", label: "GitHub or Portfolio Link" },
    { key: "has_professional_summary", label: "Professional Summary" },
    { key: "has_skills_section", label: "Dedicated Skills Section" },
    { key: "has_experience", label: "Experience Section" },
    { key: "has_education", label: "Education Section" },
    { key: "has_projects", label: "Projects Section" },
    { key: "readable_headings", label: "ATS-Readable Headings" },
    { key: "parse_quality_good", label: "High Parse Quality (No tables/columns)" },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-6 md:p-8 space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-lg">
          <FileSearch className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            ATS Formatting Checklist
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            How well robots can read and parse your document.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {checks.map((check) => {
          // Type safety assertion
          const passed = formatting[check.key as keyof ATSFormattingScore] === true;
          
          return (
            <div 
              key={check.key} 
              className={`flex items-center p-3 rounded-lg border ${
                passed 
                  ? "bg-green-50/50 border-green-100 text-green-800 dark:bg-green-900/10 dark:border-green-900/30 dark:text-green-400" 
                  : "bg-red-50/50 border-red-100 text-red-800 dark:bg-red-900/10 dark:border-red-900/30 dark:text-red-400"
              }`}
            >
              <div className={`mr-3 p-1 rounded-full ${
                passed ? "bg-green-100 dark:bg-green-900/50" : "bg-red-100 dark:bg-red-900/50"
              }`}>
                {passed ? (
                  <Check className="w-4 h-4" />
                ) : (
                  <X className="w-4 h-4" />
                )}
              </div>
              <span className="font-medium text-sm">{check.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
