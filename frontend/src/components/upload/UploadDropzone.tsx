import React, { useState, useCallback } from "react";
import { UploadCloud, FileText, X } from "lucide-react";

interface UploadDropzoneProps {
  file: File | null;
  onFileSelect: (file: File | null) => void;
  disabled?: boolean;
}

export default function UploadDropzone({ file, onFileSelect, disabled }: UploadDropzoneProps) {
  const [isDragActive, setIsDragActive] = useState(false);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragActive(true);
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    if (disabled) return;
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === "application/pdf" || droppedFile.name.toLowerCase().endsWith(".pdf")) {
        onFileSelect(droppedFile);
      } else {
        alert("Please upload a PDF file.");
      }
    }
  }, [disabled, onFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === "application/pdf" || selectedFile.name.toLowerCase().endsWith(".pdf")) {
        onFileSelect(selectedFile);
      } else {
        alert("Please upload a PDF file.");
      }
      e.target.value = "";
    }
  }, [onFileSelect]);

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Resume (PDF)
      </label>
      
      {!file ? (
        <div
          onDragEnter={handleDragEnter}
          onDragOver={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            relative flex flex-col items-center justify-center w-full p-8 
            border-2 border-dashed rounded-xl transition-all duration-200 ease-in-out
            ${disabled ? "opacity-50 cursor-not-allowed bg-gray-50 dark:bg-gray-900/50" : "cursor-pointer"}
            ${isDragActive 
              ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-500" 
              : "border-gray-200 bg-gray-50 hover:bg-gray-100 hover:border-gray-300 dark:border-gray-700 dark:bg-gray-800/50 dark:hover:bg-gray-800"
            }
          `}
        >
          <input
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileInput}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={disabled}
            title=""
          />
          
          <div className="p-3 bg-white dark:bg-gray-700 rounded-full shadow-sm mb-3 pointer-events-none">
            <UploadCloud className="w-6 h-6 text-blue-500 dark:text-blue-400" />
          </div>
          <p className="text-sm font-semibold text-gray-900 dark:text-gray-100 pointer-events-none">
            Click to upload <span className="font-normal text-gray-500 dark:text-gray-400">or drag and drop</span>
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 pointer-events-none">
            PDF (MAX. 5MB)
          </p>
        </div>
      ) : (
        <div className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="p-2 bg-blue-50 dark:bg-blue-900/30 rounded-lg shrink-0">
              <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="truncate">
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                {file.name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => onFileSelect(null)}
            disabled={disabled}
            className="relative z-10 p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Remove file"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      )}
    </div>
  );
}
