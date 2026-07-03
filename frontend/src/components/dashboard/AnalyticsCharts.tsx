"use client";

import dynamic from "next/dynamic";
import { AnalysisResponse } from "@/types/api";
import { BarChart3, PieChart as PieChartIcon } from "lucide-react";

// Lazy load Recharts components
const ResponsiveContainer = dynamic(() => import("recharts").then(mod => mod.ResponsiveContainer), { ssr: false });
const RadarChart = dynamic(() => import("recharts").then(mod => mod.RadarChart), { ssr: false });
const PolarGrid = dynamic(() => import("recharts").then(mod => mod.PolarGrid), { ssr: false });
const PolarAngleAxis = dynamic(() => import("recharts").then(mod => mod.PolarAngleAxis), { ssr: false });
const PolarRadiusAxis = dynamic(() => import("recharts").then(mod => mod.PolarRadiusAxis), { ssr: false });
const Radar = dynamic(() => import("recharts").then(mod => mod.Radar), { ssr: false });

const BarChart = dynamic(() => import("recharts").then(mod => mod.BarChart), { ssr: false });
const Bar = dynamic(() => import("recharts").then(mod => mod.Bar), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(mod => mod.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(mod => mod.YAxis), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(mod => mod.Tooltip), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then(mod => mod.CartesianGrid), { ssr: false });

const PieChart = dynamic(() => import("recharts").then(mod => mod.PieChart), { ssr: false });
const Pie = dynamic(() => import("recharts").then(mod => mod.Pie), { ssr: false });
const Cell = dynamic(() => import("recharts").then(mod => mod.Cell), { ssr: false });
const Legend = dynamic(() => import("recharts").then(mod => mod.Legend), { ssr: false });

interface AnalyticsChartsProps {
  results: AnalysisResponse;
}

export default function AnalyticsCharts({ results }: AnalyticsChartsProps) {
  
  // Radar Data
  const radarData = [
    { subject: "Required", A: results.required_skills_score, fullMark: 100 },
    { subject: "Preferred", A: results.preferred_skills_score, fullMark: 100 },
    { subject: "Semantic", A: results.semantic_score, fullMark: 100 },
    { subject: "Format", A: results.ats_score, fullMark: 100 },
    { subject: "Projects", A: results.projects_score, fullMark: 100 },
    { subject: "Experience", A: results.experience_score, fullMark: 100 },
  ];

  // Pie Data (Matched vs Missing)
  const totalRequired = results.matched_skills.length + results.missing_required.length;
  const matchCount = results.matched_skills.length;
  const missingCount = results.missing_required.length;
  
  const pieData = [
    { name: "Matched", value: matchCount },
    { name: "Missing", value: missingCount },
  ];
  const COLORS = ["#10b981", "#ef4444"]; // emerald-500, red-500

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      {/* Radar Chart Card */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-6 flex flex-col">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-5 h-5 text-gray-400" />
          <h3 className="font-semibold text-gray-900 dark:text-white">Profile Balance</h3>
        </div>
        <div className="h-64 w-full relative">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: "#6b7280", fontSize: 12 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
              <Radar
                name="Score"
                dataKey="A"
                stroke="#3b82f6" // blue-500
                fill="#3b82f6"
                fillOpacity={0.4}
              />
              <Tooltip 
                contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Pie Chart Card */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-6 flex flex-col">
        <div className="flex items-center gap-2 mb-4">
          <PieChartIcon className="w-5 h-5 text-gray-400" />
          <h3 className="font-semibold text-gray-900 dark:text-white">Skill Coverage</h3>
        </div>
        <div className="h-64 w-full relative">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
              />
              <Legend verticalAlign="bottom" height={36} iconType="circle" />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
}
