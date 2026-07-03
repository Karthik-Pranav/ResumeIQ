import React from "react";
import { LoadingState } from "@/hooks/useResumeAnalysis";
import { Loader2, UploadCloud, Search } from "lucide-react";

interface UploadProgressProps {
  loadingState: LoadingState;
  progress: number;
}

export default function UploadProgress({ loadingState, progress }: UploadProgressProps) {
  if (loadingState === "idle" || loadingState === "error" || loadingState === "complete") {
    return null;
  }

  const getStatusContent = () => {
    switch (loadingState) {
      case "uploading":
        return {
          icon: <UploadCloud className="w-5 h-5 text-blue-500 animate-pulse" />,
          title: "Uploading Resume...",
          description: `${progress}% complete`
        };
      case "analyzing":
        return {
          icon: <Search className="w-5 h-5 text-purple-500 animate-bounce" />,
          title: "Analyzing Profile...",
          description: "Extracting skills and comparing with job description"
        };
      default:
        return {
          icon: <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />,
          title: "Processing...",
          description: "Please wait"
        };
    }
  };

  const { icon, title, description } = getStatusContent();

  return (
    <div className="w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4 shadow-sm animate-in fade-in zoom-in-95 duration-300">
      <div className="flex items-center gap-4">
        <div className="p-2 bg-gray-50 dark:bg-gray-900 rounded-lg shrink-0">
          {icon}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{title}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">{description}</p>
        </div>
        <div className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          {loadingState === "uploading" ? `${progress}%` : "..."}
        </div>
      </div>
      
      {/* Progress Bar */}
      <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-1.5 mt-3 overflow-hidden">
        <div 
          className={`h-full transition-all duration-300 ease-out rounded-full ${
            loadingState === "analyzing" ? "bg-purple-500 animate-pulse" : "bg-blue-500"
          }`}
          style={{ width: loadingState === "uploading" ? `${progress}%` : '100%' }}
        />
      </div>
    </div>
  );
}
