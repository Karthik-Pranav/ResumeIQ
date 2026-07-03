import { Bot, Sparkles } from "lucide-react";

interface FeedbackCardProps {
  feedback: string;
}

export default function FeedbackCard({ feedback }: FeedbackCardProps) {
  if (!feedback) return null;

  return (
    <div className="bg-gradient-to-br from-blue-900 to-indigo-900 rounded-2xl shadow-lg p-6 md:p-8 text-white relative overflow-hidden">
      
      {/* Decorative background elements */}
      <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 rounded-full bg-white opacity-5 blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-48 h-48 rounded-full bg-blue-400 opacity-10 blur-2xl pointer-events-none" />

      <div className="relative z-10 space-y-6">
        <div className="flex items-center gap-3 border-b border-white/10 pb-4">
          <div className="p-2 bg-white/10 rounded-lg backdrop-blur-sm">
            <Bot className="w-6 h-6 text-blue-200" />
          </div>
          <div>
            <h2 className="text-xl font-bold flex items-center gap-2">
              Recruiter AI Perspective
              <Sparkles className="w-4 h-4 text-yellow-300" />
            </h2>
            <p className="text-sm text-blue-200/80">
              Personalized insights based on your ATS scan.
            </p>
          </div>
        </div>

        <div className="prose prose-invert prose-blue max-w-none">
          {/* We assume the AI feedback is plain text with newlines or basic formatting */}
          {feedback.split('\n').map((paragraph, i) => (
            <p key={i} className="text-blue-50 leading-relaxed text-[15px]">
              {paragraph}
            </p>
          ))}
        </div>
      </div>
    </div>
  );
}
