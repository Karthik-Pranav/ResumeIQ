"use client";

import { useState } from "react";
import axios from "axios";
import { AnalysisResponse } from "@/types/api";

export default function ResumeAnalyzer() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState<string>("");

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<AnalysisResponse | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !jobDescription) {
      setError("Please provide both a PDF resume and a job description.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_description", jobDescription);

    try {
      const response = await axios.post<AnalysisResponse>(
        "http://127.0.0.1:8000/analyze",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setResults(response.data);
    } catch (err: any) {
      console.error(err);
      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : JSON.stringify(err.response.data.detail)
        );
      } else {
        setError("An unexpected error occurred while analyzing the resume.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
          ResumeIQ Analysis
        </h1>
        <p className="text-gray-500 dark:text-gray-400">
          Upload your resume and details to see how well you match the job.
        </p>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="space-y-6 bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Resume (PDF)
            </label>
            <input
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 dark:text-gray-400
                file:mr-4 file:py-2 file:px-4
                file:rounded-md file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                dark:file:bg-blue-900/30 dark:file:text-blue-400
                hover:file:bg-blue-100 dark:hover:file:bg-blue-900/50
                transition-colors cursor-pointer"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Job Description
            </label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={6}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100 sm:text-sm p-3 border"
              placeholder="Paste the target job description here..."
            />
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-md text-sm border border-red-200 dark:border-red-800">
            {error}
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isLoading || !file || !jobDescription}
            className="inline-flex justify-center items-center py-2 px-6 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </>
            ) : (
              "Analyze Resume"
            )}
          </button>
        </div>
      </form>

      {/* Results Section */}
      {results && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

          {/* JD Expansion Warning Banner */}
          {results.jd_warning && (
            <div className="flex items-start gap-3 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-xl text-sm text-amber-800 dark:text-amber-300">
              <svg className="w-5 h-5 mt-0.5 shrink-0 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M12 2a10 10 0 100 20A10 10 0 0012 2z" />
              </svg>
              <p>{results.jd_warning}</p>
            </div>
          )}

          {/* Score Overview */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 flex flex-col md:flex-row items-center gap-6">
            <div className="flex flex-col items-center justify-center min-w-[150px]">
              <div className="text-5xl font-black text-blue-600 dark:text-blue-400">
                {results.match_score}
                <span className="text-2xl text-gray-400 dark:text-gray-500">/100</span>
              </div>
              <div className="text-sm font-medium text-gray-500 dark:text-gray-400 mt-1 uppercase tracking-wider">
                Match Score
              </div>
            </div>

            <div className="flex-1 w-full space-y-2">
              <div className="flex justify-between text-sm font-medium text-gray-700 dark:text-gray-300">
                <span>Relevance</span>
                <span>{results.match_score}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
                <div
                  className={`h-4 rounded-full transition-all duration-1000 ease-out ${results.match_score >= 80 ? 'bg-green-500' :
                    results.match_score >= 60 ? 'bg-blue-500' :
                      results.match_score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                  style={{ width: `${results.match_score}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                Based on semantic similarity between your resume and the job description.
                {results.matched_role && (
                  <> Role profile used: <span className="font-medium capitalize">{results.matched_role}</span>.</>
                )}
              </p>
            </div>
          </div>

          {/* Keyword Breakdown */}
          {results.keyword_breakdown && (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
                <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A2 2 0 013 12V7a2 2 0 012-2z" />
                </svg>
                Skills Analysed from Job Description
              </h3>
              <div className="grid sm:grid-cols-3 gap-4 text-sm">
                {results.keyword_breakdown.core_skills.length > 0 && (
                  <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Core Skills</p>
                    <div className="flex flex-wrap gap-1.5">
                      {results.keyword_breakdown.core_skills.map((s, i) => (
                        <span key={i} className="px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 text-xs font-medium capitalize">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {results.keyword_breakdown.tools.length > 0 && (
                  <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Tools</p>
                    <div className="flex flex-wrap gap-1.5">
                      {results.keyword_breakdown.tools.map((t, i) => (
                        <span key={i} className="px-2 py-0.5 rounded-full bg-purple-100 dark:bg-purple-900/40 text-purple-800 dark:text-purple-300 text-xs font-medium capitalize">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {results.keyword_breakdown.concepts.length > 0 && (
                  <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Concepts</p>
                    <div className="flex flex-wrap gap-1.5">
                      {results.keyword_breakdown.concepts.map((c, i) => (
                        <span key={i} className="px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs font-medium capitalize">
                          {c}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Strengths & Gaps */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-green-700 dark:text-green-400 mb-4 flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                Key Strengths
              </h3>
              {results.strengths.length > 0 ? (
                <ul className="space-y-3">
                  {results.strengths.map((s, i) => (
                    <li key={i} className="flex gap-2 text-gray-700 dark:text-gray-300 text-sm">
                      <span className="text-green-500 mt-0.5">•</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500 italic">No significant strengths identified.</p>
              )}
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-red-700 dark:text-red-400 mb-4 flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                Missing Skills (Gaps)
              </h3>
              {results.gaps.length > 0 ? (
                <ul className="space-y-3">
                  {results.gaps.map((g, i) => (
                    <li key={i} className="flex gap-2 text-gray-700 dark:text-gray-300 text-sm">
                      <span className="text-red-400 mt-0.5">•</span>
                      <span className="capitalize">{g}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500 italic">No major gaps identified!</p>
              )}
            </div>
          </div>

          {/* Matched Sections */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 border-b border-gray-100 dark:border-gray-700 pb-3">
              Top Matched Sections
            </h3>

            {results.matched_sections.length > 0 ? (
              <div className="space-y-6">
                {results.matched_sections.map((section, idx) => (
                  <div key={idx} className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-5 border border-gray-100 dark:border-gray-800 relative">
                    <div className="absolute top-4 right-4 bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 text-xs font-bold px-2 py-1 rounded">
                      Sim: {section.similarity_score.toFixed(2)}
                    </div>

                    <div className="grid md:grid-cols-2 gap-6 mt-2">
                      <div>
                        <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Resume Snippet</h4>
                        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed bg-white border border-gray-200 dark:border-gray-700 dark:bg-gray-800 p-3 rounded shadow-sm">
                          &ldquo;{section.resume_chunk}&rdquo;
                        </p>
                      </div>
                      <div>
                        <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Relevant Job Requirement</h4>
                        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed bg-white border border-gray-200 dark:border-gray-700 dark:bg-gray-800 p-3 rounded shadow-sm">
                          &ldquo;{section.job_chunk}&rdquo;
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 italic">No significant matching sections found.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
