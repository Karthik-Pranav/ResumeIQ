"use client";

import React from "react";
import UploadDropzone from "./UploadDropzone";
import UploadProgress from "./UploadProgress";
import { LoadingState } from "@/hooks/useResumeAnalysis";
import { AlertCircle } from "lucide-react";

interface UploadFormProps {
  file: File | null;
  jobDescription: string;
  loadingState: LoadingState;
  uploadProgress: number;
  error: string | null;
  onFileSelect: (file: File | null) => void;
  onJobDescriptionChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSubmit: (e: React.FormEvent) => void;
}

export default function UploadForm({
  file,
  jobDescription,
  loadingState,
  uploadProgress,
  error,
  onFileSelect,
  onJobDescriptionChange,
  onSubmit,
}: UploadFormProps) {
  const isBusy = loadingState === "uploading" || loadingState === "analyzing";

  return (
    <form onSubmit={onSubmit} className="space-y-6">
      
      <UploadDropzone 
        file={file} 
        onFileSelect={onFileSelect} 
        disabled={isBusy}
      />

      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Job Description
          </label>
          <textarea
            value={jobDescription}
            onChange={onJobDescriptionChange}
            disabled={isBusy}
            rows={5}
            className="block w-full rounded-lg border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900/50 focus:bg-white dark:focus:bg-gray-900 focus:border-blue-500 focus:ring-blue-500 dark:text-gray-100 sm:text-sm p-4 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            placeholder="Paste the target job description here..."
          />
        </div>
      </div>

      {error && (
        <div className="flex items-start gap-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-sm text-red-800 dark:text-red-300 animate-in fade-in zoom-in-95 duration-200">
          <AlertCircle className="w-5 h-5 shrink-0 text-red-500" />
          <p className="mt-0.5">{error}</p>
        </div>
      )}

      {isBusy ? (
        <UploadProgress loadingState={loadingState} progress={uploadProgress} />
      ) : (
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={!file || !jobDescription.trim()}
            className="inline-flex justify-center items-center py-2.5 px-6 border border-transparent text-sm font-medium rounded-lg text-white bg-black hover:bg-gray-800 dark:bg-white dark:text-black dark:hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-900 dark:focus:ring-white disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
          >
            Analyze Resume
          </button>
        </div>
      )}
    </form>
  );
}
