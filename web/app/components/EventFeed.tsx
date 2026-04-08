"use client";

import { AlertTriangle, Zap, Globe, Swords, TrendingUp, Shield } from "lucide-react";

interface SimEvent {
  title: string;
  description: string;
  category: string;
  severity: string;
  source_country?: string;
  year: number;
  turn: number;
}

interface Props {
  events: SimEvent[];
}

const SEVERITY_STYLES: Record<string, string> = {
  low: "border-l-gray-500 bg-gray-900/20",
  medium: "border-l-yellow-500 bg-yellow-900/10",
  high: "border-l-red-500 bg-red-900/10",
  critical: "border-l-red-600 bg-red-900/20 glow-red",
};

const CATEGORY_ICONS: Record<string, typeof Globe> = {
  military: Swords,
  economic: TrendingUp,
  diplomatic: Globe,
  political: Shield,
  technological: Zap,
  crisis: AlertTriangle,
  social: Globe,
  environmental: Globe,
};

export default function EventFeed({ events }: Props) {
  if (events.length === 0) return null;

  return (
    <div className="bg-[#1a1a2e] border border-[#2a2a3e] rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-[#2a2a3e] flex items-center gap-2">
        <AlertTriangle className="w-5 h-5 text-red-400" />
        <h2 className="text-lg font-bold">Breaking Events</h2>
        <span className="text-xs text-[#888] ml-auto">{events.length} events</span>
      </div>
      <div className="max-h-80 overflow-y-auto scrollbar-thin">
        {events.map((event, i) => {
          const Icon = CATEGORY_ICONS[event.category] || Globe;
          const style = SEVERITY_STYLES[event.severity] || SEVERITY_STYLES.medium;
          return (
            <div
              key={i}
              className={`border-l-4 px-4 py-3 ${style} animate-slide-up`}
              style={{ animationDelay: `${i * 50}ms` }}
            >
              <div className="flex items-center gap-2 mb-1">
                <Icon className="w-4 h-4 text-[#888]" />
                <span className="text-xs uppercase text-[#888]">{event.category}</span>
                <span className={`text-xs font-bold uppercase ${
                  event.severity === "critical" ? "text-red-400" : "text-yellow-400"
                }`}>
                  {event.severity}
                </span>
                {event.source_country && (
                  <span className="text-xs text-cyan-400 ml-auto">{event.source_country}</span>
                )}
              </div>
              <p className="text-sm font-bold">{event.title}</p>
              <p className="text-xs text-[#888] mt-1">{event.description}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
