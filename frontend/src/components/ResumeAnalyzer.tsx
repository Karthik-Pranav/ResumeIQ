"use client";

import { useResumeAnalysis } from "@/hooks/useResumeAnalysis";
import UploadForm from "./upload/UploadForm";
import Dashboard from "./dashboard/Dashboard";
import LoadingTimeline from "./dashboard/LoadingTimeline";
import { FileSearch } from "lucide-react";

export default function ResumeAnalyzer() {
  const {
    file,
    jobDescription,
    loadingState,
    uploadProgress,
    error,
    results,
    handleFileSelect,
    handleJobDescriptionChange,
    handleSubmit,
  } = useResumeAnalysis();

  return (
    <div className="max-w-5xl mx-auto p-4 sm:p-6 lg:p-8 space-y-12">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white">
          ResumeIQ
        </h1>
        <p className="text-lg text-gray-500 dark:text-gray-400 max-w-2xl mx-auto">
          Match your resume against any job description with ATS-grade precision.
        </p>
      </div>

      {/* Input Form */}
      <UploadForm
        file={file}
        jobDescription={jobDescription}
        loadingState={loadingState}
        uploadProgress={uploadProgress}
        error={error}
        onFileSelect={handleFileSelect}
        onJobDescriptionChange={handleJobDescriptionChange}
        onSubmit={handleSubmit}
      />

      {/* Results Section or Empty State */}
      {loadingState === "analyzing" || loadingState === "uploading" ? (
        <LoadingTimeline isLoading={true} />
      ) : results ? (
        <Dashboard results={results} />
      ) : loadingState === "idle" && !error ? (
        <div className="flex flex-col items-center justify-center p-12 text-center border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-2xl bg-gray-50/50 dark:bg-gray-900/20">
          <FileSearch className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No results yet</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 max-w-sm">
            {!file ? "Upload a PDF to begin analysis." : "Paste a job description and click analyze to check your ATS match."}
          </p>
        </div>
      ) : null}
    </div>
  );
}
