"use client";

import { LeaderDecision } from "../lib/api";
import { Brain, MessageSquare, Swords, Shield, TrendingUp, Eye, Handshake } from "lucide-react";

interface Props {
  countryCode: string;
  decision: LeaderDecision;
}

const MOOD_CONFIG: Record<string, { color: string; label: string }> = {
  confident: { color: "text-green-400 border-green-400/30", label: "CONFIDENT" },
  anxious: { color: "text-yellow-400 border-yellow-400/30", label: "ANXIOUS" },
  aggressive: { color: "text-red-400 border-red-400/30", label: "AGGRESSIVE" },
  defensive: { color: "text-blue-400 border-blue-400/30", label: "DEFENSIVE" },
  opportunistic: { color: "text-purple-400 border-purple-400/30", label: "OPPORTUNISTIC" },
  desperate: { color: "text-red-600 border-red-600/30", label: "DESPERATE" },
};

const ACTION_ICONS: Record<string, typeof Swords> = {
  military: Swords,
  diplomacy: Handshake,
  economic: TrendingUp,
  intelligence: Eye,
  threaten: Swords,
  negotiate: Handshake,
  alliance: Shield,
};

export default function LeaderCard({ countryCode, decision }: Props) {
  const mood = MOOD_CONFIG[decision.mood] || MOOD_CONFIG.confident;

  return (
    <div className={`bg-[#1a1a2e] border rounded-lg overflow-hidden animate-slide-up ${mood.color.split(" ")[1]}`}>
      <div className="px-4 py-3 border-b border-[#2a2a3e] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl font-bold">{countryCode}</span>
        </div>
        <span className={`text-xs font-bold px-2 py-1 rounded ${mood.color}`}>
          {mood.label}
        </span>
      </div>

      <div className="p-4 space-y-3">
        <div className="flex items-start gap-2">
          <MessageSquare className="w-4 h-4 text-cyan-400 mt-1 shrink-0" />
          <p className="text-sm italic text-[#ccc]">&ldquo;{decision.public_statement}&rdquo;</p>
        </div>

        {decision.actions.length > 0 && (
          <div className="space-y-2">
            <div className="text-xs text-[#888] uppercase tracking-wider">Actions</div>
            {decision.actions.map((action, i) => {
              const Icon = ACTION_ICONS[action.type] || Brain;
              const intensity = action.intensity ?? 0.5;
              return (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <Icon className="w-4 h-4 text-[#888] shrink-0" />
                  <div className="flex-1">
                    <span className="text-[#aaa] uppercase text-xs">
                      {action.type.replace("_", " ")}
                    </span>
                    <span className="text-[#666] mx-1">&rarr;</span>
                    <span className="text-cyan-400">{action.target}</span>
                    <p className="text-[#888] text-xs mt-0.5">{action.detail}</p>
                  </div>
                  <div className="w-16 h-1.5 bg-[#2a2a3e] rounded-full overflow-hidden shrink-0">
                    <div
                      className={`h-full rounded-full ${
                        intensity > 0.7 ? "bg-red-500" : intensity > 0.4 ? "bg-yellow-500" : "bg-green-500"
                      }`}
                      style={{ width: `${intensity * 100}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <details className="group">
          <summary className="text-xs text-[#666] cursor-pointer hover:text-[#888]">
            <Brain className="inline w-3 h-3 mr-1" />
            Inner Thoughts
          </summary>
          <p className="text-xs text-[#666] mt-2 pl-4 border-l border-[#2a2a3e]">
            {decision.inner_thoughts}
          </p>
        </details>
      </div>
    </div>
  );
}
