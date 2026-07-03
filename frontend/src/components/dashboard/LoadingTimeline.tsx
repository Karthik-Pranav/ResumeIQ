"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, Cpu, Search, CheckCircle2, Bot } from "lucide-react";

interface LoadingTimelineProps {
  isLoading: boolean;
}

const STAGES = [
  { id: 1, label: "Parsing Resume", icon: FileText, duration: 1500 },
  { id: 2, label: "Extracting Skills", icon: Search, duration: 2000 },
  { id: 3, label: "Running Semantic Analysis", icon: Cpu, duration: 2500 },
  { id: 4, label: "Calculating ATS Score", icon: CheckCircle2, duration: 1500 },
  { id: 5, label: "Generating AI Feedback", icon: Bot, duration: 3000 },
];

export default function LoadingTimeline({ isLoading }: LoadingTimelineProps) {
  const [currentStage, setCurrentStage] = useState(0);

  useEffect(() => {
    if (!isLoading) {
      setCurrentStage(0);
      return;
    }

    let timeoutId: NodeJS.Timeout;
    
    const runStages = (stageIndex: number) => {
      if (stageIndex >= STAGES.length) return;
      
      setCurrentStage(stageIndex);
      
      // If we're on the last stage, just stay there until loading finishes
      if (stageIndex < STAGES.length - 1) {
        timeoutId = setTimeout(() => {
          runStages(stageIndex + 1);
        }, STAGES[stageIndex].duration);
      }
    };

    runStages(0);

    return () => clearTimeout(timeoutId);
  }, [isLoading]);

  if (!isLoading) return null;

  return (
    <div className="w-full max-w-lg mx-auto py-12 px-6">
      <div className="space-y-6">
        {STAGES.map((stage, index) => {
          const isActive = index === currentStage;
          const isComplete = index < currentStage;
          const isPending = index > currentStage;
          
          const Icon = stage.icon;
          
          return (
            <div key={stage.id} className="relative flex items-center gap-4">
              {/* Connecting Line */}
              {index < STAGES.length - 1 && (
                <div 
                  className={`absolute left-[1.125rem] top-10 bottom-[-1.5rem] w-0.5 
                  ${isComplete ? "bg-blue-500 dark:bg-blue-400" : "bg-gray-200 dark:bg-gray-700"}
                  transition-colors duration-500`}
                />
              )}
              
              <div 
                className={`relative z-10 flex h-9 w-9 items-center justify-center rounded-full border-2 
                  ${isActive ? "border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400" : 
                    isComplete ? "border-blue-500 bg-blue-500 text-white" : 
                    "border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800 text-gray-400"}
                  transition-all duration-300`}
              >
                {isActive ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                  >
                    <Icon className="h-4 w-4" />
                  </motion.div>
                ) : (
                  <Icon className="h-4 w-4" />
                )}
              </div>
              
              <div className="flex flex-col">
                <span 
                  className={`text-sm font-medium transition-colors duration-300
                    ${isActive ? "text-blue-700 dark:text-blue-400" : 
                      isComplete ? "text-gray-900 dark:text-white" : 
                      "text-gray-500 dark:text-gray-400"}`}
                >
                  {stage.label}
                </span>
                
                <AnimatePresence>
                  {isActive && (
                    <motion.span 
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      className="text-xs text-blue-600/70 dark:text-blue-400/70"
                    >
                      Working...
                    </motion.span>
                  )}
                </AnimatePresence>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
