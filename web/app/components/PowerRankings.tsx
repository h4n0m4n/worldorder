"use client";

import { Country } from "../lib/api";
import { Shield, Zap, Users, TrendingUp, TrendingDown, AlertTriangle } from "lucide-react";

interface Props {
  countries: Country[];
}

export default function PowerRankings({ countries }: Props) {
  return (
    <div className="bg-[#1a1a2e] border border-[#2a2a3e] rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-[#2a2a3e] flex items-center gap-2">
        <Shield className="w-5 h-5 text-yellow-400" />
        <h2 className="text-lg font-bold">Global Power Rankings</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[#2a2a3e] text-[#888]">
              <th className="px-4 py-2 text-left w-8">#</th>
              <th className="px-4 py-2 text-left">Country</th>
              <th className="px-4 py-2 text-right">Power</th>
              <th className="px-4 py-2 text-right">GDP</th>
              <th className="px-4 py-2 text-center">Military</th>
              <th className="px-4 py-2 text-center">Stability</th>
              <th className="px-4 py-2 text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            {countries.map((c, i) => (
              <tr
                key={c.code}
                className="border-b border-[#2a2a3e]/50 hover:bg-[#2a2a3e]/30 transition-colors"
              >
                <td className="px-4 py-2">
                  <span className={i < 3 ? "text-yellow-400 font-bold" : "text-[#888]"}>
                    {i + 1}
                  </span>
                </td>
                <td className="px-4 py-2">
                  <span className="font-bold">{c.name}</span>
                  <span className="text-[#888] ml-2">({c.code})</span>
                  {c.nuclear && <Zap className="inline w-3 h-3 ml-1 text-purple-400" />}
                </td>
                <td className="px-4 py-2 text-right font-mono">
                  {c.composite_power.toFixed(1)}
                </td>
                <td className="px-4 py-2 text-right font-mono">
                  ${c.gdp_trillion.toFixed(1)}T
                </td>
                <td className="px-4 py-2 text-center">
                  <ProgressBar value={c.military_power} color="red" />
                </td>
                <td className="px-4 py-2 text-center">
                  <ProgressBar value={c.stability} color={c.stability > 0.6 ? "green" : c.stability > 0.4 ? "yellow" : "red"} />
                </td>
                <td className="px-4 py-2 text-center">
                  <StatusBadges country={c} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ProgressBar({ value, color }: { value: number; color: string }) {
  const colorMap: Record<string, string> = {
    red: "bg-red-500",
    green: "bg-green-500",
    yellow: "bg-yellow-500",
    blue: "bg-blue-500",
  };
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-2 bg-[#2a2a3e] rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${colorMap[color] || "bg-blue-500"}`}
          style={{ width: `${value * 100}%` }}
        />
      </div>
      <span className="text-xs font-mono text-[#888]">{(value * 100).toFixed(0)}%</span>
    </div>
  );
}

function StatusBadges({ country }: { country: Country }) {
  const badges: React.ReactElement[] = [];
  if (country.gdp_growth !== undefined && country.gdp_growth < 0) {
    badges.push(
      <span key="rec" className="text-xs px-1.5 py-0.5 bg-red-900/50 text-red-400 rounded">
        <TrendingDown className="inline w-3 h-3" /> REC
      </span>
    );
  }
  if (country.inflation !== undefined && country.inflation > 10) {
    badges.push(
      <span key="inf" className="text-xs px-1.5 py-0.5 bg-yellow-900/50 text-yellow-400 rounded">
        <TrendingUp className="inline w-3 h-3" /> INF
      </span>
    );
  }
  if (country.stability < 0.4) {
    badges.push(
      <span key="ust" className="text-xs px-1.5 py-0.5 bg-red-900/50 text-red-400 rounded">
        <AlertTriangle className="inline w-3 h-3" /> UNSTABLE
      </span>
    );
  }
  if (badges.length === 0) {
    return <span className="text-xs text-green-400">Stable</span>;
  }
  return <div className="flex gap-1 justify-center">{badges}</div>;
}
