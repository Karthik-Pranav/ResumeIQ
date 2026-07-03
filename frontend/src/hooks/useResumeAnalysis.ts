import { useState, useCallback } from "react";
import { AnalysisResponse } from "@/types/api";
import { analyzeResume } from "@/services/api";

export type LoadingState = "idle" | "uploading" | "analyzing" | "complete" | "error";

export function useResumeAnalysis() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState<string>("");

  const [loadingState, setLoadingState] = useState<LoadingState>("idle");
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<AnalysisResponse | null>(null);

  const handleFileSelect = useCallback((selectedFile: File | null) => {
    setFile(selectedFile);
    if (error) setError(null);
  }, [error]);

  const handleJobDescriptionChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setJobDescription(e.target.value);
    if (error) setError(null);
  }, [error]);

  const resetState = useCallback(() => {
    setFile(null);
    setJobDescription("");
    setLoadingState("idle");
    setUploadProgress(0);
    setError(null);
    setResults(null);
  }, []);

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!file || !jobDescription.trim()) {
      setError("Please provide both a PDF resume and a job description.");
      setLoadingState("error");
      return;
    }

    setLoadingState("uploading");
    setUploadProgress(0);
    setError(null);
    setResults(null);

    try {
      const data = await analyzeResume(file, jobDescription, (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
          if (percentCompleted === 100) {
            setLoadingState("analyzing");
          }
        }
      });
      
      setResults(data);
      setLoadingState("complete");
    } catch (err: unknown) {
      console.error(err);
      setLoadingState("error");
      
      // Error mapping for better UX
      if (typeof err === "object" && err !== null && "response" in err) {
        const axiosErr = err as any;
        const status = axiosErr.response?.status;
        const detail = axiosErr.response?.data?.detail;
        
        if (status === 413) {
          setError("File too large. Please upload a PDF smaller than 5MB.");
          return;
        } else if (status === 429) {
          setError("You've reached the rate limit. Please try again in a moment.");
          return;
        }
        
        if (detail) {
          setError(typeof detail === "string" ? detail : JSON.stringify(detail));
          return;
        }
      }
      
      if (err instanceof Error && err.message === "Network Error") {
        setError("Network error. The backend server might be unavailable.");
        return;
      }
      
      setError("Analysis failed. An unexpected error occurred.");
    }
  };

  return {
    file,
    jobDescription,
    loadingState,
    uploadProgress,
    error,
    results,
    handleFileSelect,
    handleJobDescriptionChange,
    handleSubmit,
    resetState,
  };
}
