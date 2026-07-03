import { motion } from "framer-motion";
import { 
  CheckSquare, 
  Lightbulb, 
  BrainCircuit, 
  FileCheck, 
  FolderGit2, 
  Briefcase, 
  GraduationCap 
} from "lucide-react";
import { AnalysisResponse } from "@/types/api";

interface ScoreCardsProps {
  results: AnalysisResponse;
}

export default function ScoreCards({ results }: ScoreCardsProps) {
  const cards = [
    {
      title: "Required Skills",
      score: results.required_skills_score,
      icon: CheckSquare,
      desc: "Match of mandatory job requirements."
    },
    {
      title: "Preferred Skills",
      score: results.preferred_skills_score,
      icon: Lightbulb,
      desc: "Bonus points for nice-to-have skills."
    },
    {
      title: "Semantic Match",
      score: results.semantic_score,
      icon: BrainCircuit,
      desc: "Contextual alignment of experience to duties."
    },
    {
      title: "ATS Format",
      score: results.ats_score,
      icon: FileCheck,
      desc: "Readability by automated tracking systems."
    },
    {
      title: "Projects",
      score: results.projects_score,
      icon: FolderGit2,
      desc: "Relevance of showcased portfolio work."
    },
    {
      title: "Experience",
      score: results.experience_score,
      icon: Briefcase,
      desc: "Alignment of past professional roles."
    },
    {
      title: "Education",
      score: results.education_score,
      icon: GraduationCap,
      desc: "Fulfillment of academic requirements."
    }
  ];

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600 dark:text-green-400";
    if (score >= 50) return "text-blue-600 dark:text-blue-400";
    return "text-orange-600 dark:text-orange-400";
  };

  return (
    <motion.div 
      variants={container}
      initial="hidden"
      animate="show"
      className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4"
    >
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <motion.div 
            key={idx}
            variants={item}
            className="flex flex-col bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start mb-4">
              <div className="p-2 bg-gray-50 dark:bg-gray-900 rounded-lg">
                <Icon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </div>
              <span className={`text-xl font-bold ${getScoreColor(card.score)}`}>
                {card.score}%
              </span>
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-sm">
              {card.title}
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {card.desc}
            </p>
          </motion.div>
        );
      })}
    </motion.div>
  );
}
