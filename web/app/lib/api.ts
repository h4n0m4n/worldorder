const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Country {
  code: string;
  name: string;
  composite_power: number;
  gdp_trillion: number;
  gdp_growth?: number;
  inflation?: number;
  military_power: number;
  stability: number;
  population_million: number;
  nuclear: boolean;
  alliances: string[];
  relations?: Record<string, string>;
}

export interface Leader {
  id: string;
  name: string;
  country: string;
  title: string;
  ideology: string;
  risk_tolerance: number;
  traits: string[];
}

export interface Scenario {
  id: string;
  title: string;
  description: string;
  start_year: number;
  key_countries: string[];
  initial_events: Array<{ title: string; category: string; severity: string }>;
}

export interface SimulationState {
  turn: number;
  year: number;
  countries: Country[];
  total_events: number;
}

export interface TurnResult {
  turn: number;
  year: number;
  continue: boolean;
  decisions: Record<string, LeaderDecision>;
  power_rankings: Array<{ code: string; name: string; power: number }>;
}

export interface LeaderDecision {
  inner_thoughts: string;
  public_statement: string;
  actions: Array<{
    type: string;
    target: string;
    detail: string;
    intensity?: number;
  }>;
  mood: string;
}

export interface SimulationConfig {
  era?: string;
  start_year?: number;
  end_year?: number;
  max_turns?: number;
  time_scale?: string;
  game_mode?: string;
  player_country?: string;
  llm_provider?: string;
  llm_model?: string;
  seed?: number;
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API Error ${res.status}: ${err}`);
  }
  return res.json();
}

export const api = {
  health: () => apiFetch<{ name: string; version: string }>("/"),
  countries: () => apiFetch<Country[]>("/countries"),
  leaders: () => apiFetch<Leader[]>("/leaders"),
  scenarios: () => apiFetch<Scenario[]>("/scenarios"),
  history: () => apiFetch<Record<string, { events: Array<{ year: number; title: string; countries: string[]; category: string }> }>>("/history"),
  providers: () => apiFetch<{ providers: string[] }>("/providers"),

  createSimulation: (config: SimulationConfig) =>
    apiFetch<{ status: string; countries: number; leaders: number }>("/simulation/create", {
      method: "POST",
      body: JSON.stringify(config),
    }),

  runTurn: () => apiFetch<TurnResult>("/simulation/turn", { method: "POST" }),

  getState: () => apiFetch<SimulationState>("/simulation/state"),

  injectCrisis: (crisis: { title: string; description: string; target_countries?: string[] }) =>
    apiFetch<{ status: string }>("/simulation/crisis", {
      method: "POST",
      body: JSON.stringify(crisis),
    }),
};
