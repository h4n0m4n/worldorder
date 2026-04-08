"use client";

import { useState } from "react";
import { Play, Pause, SkipForward, Zap, Settings } from "lucide-react";

interface Props {
  onStart: (config: SimConfig) => void;
  onNextTurn: () => void;
  onInjectCrisis: (title: string, description: string) => void;
  isRunning: boolean;
  isLoading: boolean;
  turn: number;
  year: number;
  maxTurns: number;
}

interface SimConfig {
  era: string;
  start_year: number;
  end_year: number;
  max_turns: number;
  llm_provider: string;
  llm_model: string;
}

export default function SimulationControls({
  onStart,
  onNextTurn,
  onInjectCrisis,
  isRunning,
  isLoading,
  turn,
  year,
  maxTurns,
}: Props) {
  const [showConfig, setShowConfig] = useState(!isRunning);
  const [showCrisis, setShowCrisis] = useState(false);
  const [config, setConfig] = useState<SimConfig>({
    era: "contemporary",
    start_year: 2025,
    end_year: 2100,
    max_turns: 50,
    llm_provider: "ollama",
    llm_model: "llama3.1",
  });
  const [crisisTitle, setCrisisTitle] = useState("");
  const [crisisDesc, setCrisisDesc] = useState("");

  return (
    <div className="bg-[#1a1a2e] border border-[#2a2a3e] rounded-lg p-4 space-y-4">
      {isRunning && (
        <div className="flex items-center justify-between">
          <div>
            <span className="text-2xl font-bold text-yellow-400">{year}</span>
            <span className="text-[#888] ml-3">Turn {turn + 1}/{maxTurns}</span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={onNextTurn}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:bg-[#2a2a3e] disabled:text-[#666] rounded-lg transition-colors font-bold"
            >
              {isLoading ? (
                <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Processing...</>
              ) : (
                <><SkipForward className="w-4 h-4" /> Next Turn</>
              )}
            </button>
            <button
              onClick={() => setShowCrisis(!showCrisis)}
              className="flex items-center gap-2 px-4 py-2 bg-red-600/80 hover:bg-red-500 rounded-lg transition-colors"
            >
              <Zap className="w-4 h-4" /> Inject Crisis
            </button>
          </div>
        </div>
      )}

      {showCrisis && (
        <div className="border border-red-500/30 rounded-lg p-3 space-y-2">
          <input
            type="text"
            placeholder="Crisis title..."
            value={crisisTitle}
            onChange={(e) => setCrisisTitle(e.target.value)}
            className="w-full bg-[#0a0a0f] border border-[#2a2a3e] rounded px-3 py-2 text-sm"
          />
          <textarea
            placeholder="Describe the crisis..."
            value={crisisDesc}
            onChange={(e) => setCrisisDesc(e.target.value)}
            className="w-full bg-[#0a0a0f] border border-[#2a2a3e] rounded px-3 py-2 text-sm h-20 resize-none"
          />
          <button
            onClick={() => {
              if (crisisTitle) {
                onInjectCrisis(crisisTitle, crisisDesc);
                setCrisisTitle("");
                setCrisisDesc("");
                setShowCrisis(false);
              }
            }}
            className="px-4 py-2 bg-red-600 hover:bg-red-500 rounded text-sm font-bold"
          >
            Launch Crisis
          </button>
        </div>
      )}

      {!isRunning && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 mb-2">
            <Settings className="w-5 h-5 text-[#888]" />
            <h3 className="font-bold">Simulation Configuration</h3>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[#888]">Era</label>
              <select
                value={config.era}
                onChange={(e) => setConfig({ ...config, era: e.target.value })}
                className="w-full bg-[#0a0a0f] border border-[#2a2a3e] rounded px-3 py-2 text-sm"
              >
                <option value="ancient">Ancient</option>
                <option value="medieval">Medieval</option>
                <option value="early_modern">Early Modern</option>
                <option value="modern">Modern</option>
                <option value="contemporary">Contemporary</option>
                <option value="future">Future</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-[#888]">LLM Provider</label>
              <select
                value={config.llm_provider}
                onChange={(e) => setConfig({ ...config, llm_provider: e.target.value })}
                className="w-full bg-[#0a0a0f] border border-[#2a2a3e] rounded px-3 py-2 text-sm"
              >
                <option value="ollama">Ollama (Local)</option>
                <option value="groq">Groq (Free API)</option>
                <option value="openrouter">OpenRouter</option>
                <option value="openai">OpenAI</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-[#888]">Start Year</label>
              <input
                type="number"
                value={config.start_year}
                onChange={(e) => setConfig({ ...config, start_year: parseInt(e.target.value) })}
                className="w-full bg-[#0a0a0f] border border-[#2a2a3e] rounded px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="text-xs text-[#888]">Max Turns</label>
              <input
                type="number"
                value={config.max_turns}
                onChange={(e) => setConfig({ ...config, max_turns: parseInt(e.target.value) })}
                className="w-full bg-[#0a0a0f] border border-[#2a2a3e] rounded px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="text-xs text-[#888]">Model</label>
              <input
                type="text"
                value={config.llm_model}
                onChange={(e) => setConfig({ ...config, llm_model: e.target.value })}
                className="w-full bg-[#0a0a0f] border border-[#2a2a3e] rounded px-3 py-2 text-sm"
              />
            </div>
          </div>
          <button
            onClick={() => onStart(config)}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-cyan-600 hover:bg-cyan-500 rounded-lg transition-colors font-bold text-lg"
          >
            <Play className="w-5 h-5" /> Launch Simulation
          </button>
        </div>
      )}
    </div>
  );
}
