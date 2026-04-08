"use client";

import { useState, useCallback } from "react";
import { Globe, Zap, Shield, Brain, History, ChevronRight } from "lucide-react";
import PowerRankings from "./components/PowerRankings";
import LeaderCard from "./components/LeaderCard";
import EventFeed from "./components/EventFeed";
import SimulationControls from "./components/SimulationControls";
import { api, Country, LeaderDecision, TurnResult, SimulationConfig } from "./lib/api";

interface SimState {
  running: boolean;
  turn: number;
  year: number;
  maxTurns: number;
  countries: Country[];
  decisions: Record<string, LeaderDecision>;
  events: any[];
  history: TurnResult[];
}

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sim, setSim] = useState<SimState>({
    running: false,
    turn: 0,
    year: 2025,
    maxTurns: 50,
    countries: [],
    decisions: {},
    events: [],
    history: [],
  });

  const handleStart = useCallback(async (config: SimulationConfig) => {
    setLoading(true);
    setError(null);
    try {
      await api.createSimulation(config);
      const state = await api.getState();
      setSim({
        running: true,
        turn: state.turn,
        year: state.year,
        maxTurns: config.max_turns || 50,
        countries: state.countries,
        decisions: {},
        events: [],
        history: [],
      });
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleNextTurn = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.runTurn();
      const state = await api.getState();
      setSim((prev) => ({
        ...prev,
        turn: state.turn,
        year: state.year,
        countries: state.countries,
        decisions: result.decisions,
        events: (result as any).events || prev.events,
        history: [...prev.history, result],
        running: result.continue,
      }));
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleInjectCrisis = useCallback(async (title: string, description: string) => {
    try {
      await api.injectCrisis({ title, description });
    } catch (e: any) {
      setError(e.message);
    }
  }, []);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-[#2a2a3e] bg-[#0a0a0f]/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Globe className="w-8 h-8 text-cyan-400" />
            <div>
              <h1 className="text-xl font-bold tracking-wider">WORLD ORDER</h1>
              <p className="text-xs text-[#888]">AI-Powered Geopolitical Simulation</p>
            </div>
          </div>
          <div className="flex items-center gap-4 text-sm text-[#888]">
            {sim.running && (
              <>
                <span className="flex items-center gap-1">
                  <History className="w-4 h-4" /> Year {sim.year}
                </span>
                <span className="flex items-center gap-1">
                  <Zap className="w-4 h-4" /> Turn {sim.turn + 1}
                </span>
                <span className="flex items-center gap-1">
                  <Shield className="w-4 h-4" /> {sim.countries.length} Nations
                </span>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Hero (when not running) */}
        {!sim.running && !loading && (
          <div className="text-center py-12 space-y-4">
            <h2 className="text-4xl font-bold">
              <span className="text-cyan-400">Simulate</span> the Future of{" "}
              <span className="text-yellow-400">Geopolitics</span>
            </h2>
            <p className="text-[#888] max-w-2xl mx-auto text-lg">
              Real world leaders as AI agents. Real political personalities.
              From ancient civilizations to 2100. Watch them negotiate, threaten,
              and reshape the world order.
            </p>
            <div className="flex justify-center gap-6 text-sm text-[#888] pt-4">
              <div className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-400" />
                <span>AI-Powered Leaders</span>
              </div>
              <div className="flex items-center gap-2">
                <Globe className="w-5 h-5 text-cyan-400" />
                <span>21 Nations</span>
              </div>
              <div className="flex items-center gap-2">
                <History className="w-5 h-5 text-yellow-400" />
                <span>3000 BC → 2100 AD</span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-red-400" />
                <span>What-If Scenarios</span>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-4 text-red-400">
            {error}
          </div>
        )}

        {/* Controls */}
        <SimulationControls
          onStart={handleStart}
          onNextTurn={handleNextTurn}
          onInjectCrisis={handleInjectCrisis}
          isRunning={sim.running}
          isLoading={loading}
          turn={sim.turn}
          year={sim.year}
          maxTurns={sim.maxTurns}
        />

        {/* Simulation View */}
        {sim.running && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left: Power Rankings */}
            <div className="lg:col-span-2">
              <PowerRankings countries={sim.countries} />
            </div>

            {/* Right: Events */}
            <div>
              <EventFeed events={sim.events} />
            </div>

            {/* Leader Decisions */}
            {Object.keys(sim.decisions).length > 0 && (
              <div className="lg:col-span-3">
                <div className="flex items-center gap-2 mb-4">
                  <Brain className="w-5 h-5 text-purple-400" />
                  <h2 className="text-lg font-bold">Leader Decisions — Year {sim.year}</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(sim.decisions).map(([code, decision]) => (
                    <LeaderCard key={code} countryCode={code} decision={decision} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-[#2a2a3e] mt-12 py-6 text-center text-sm text-[#666]">
        <p>
          WORLD ORDER — History doesn&apos;t repeat itself, but it rhymes. Now you can hear the next verse.
        </p>
        <p className="mt-1">
          <a href="https://github.com/h4n0m4n/worldorder" className="text-cyan-400 hover:underline">
            GitHub
          </a>
          {" · "}Open Source · MIT License
        </p>
      </footer>
    </div>
  );
}
