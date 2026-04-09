"""WORLD ORDER — Modern Web Interface.

Persistent simulation state, WebSocket live updates, cinematic UI.
Single-file FastAPI app — no build step, no npm.
"""

import asyncio
import json
from pathlib import Path as _Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from engine.config import SimulationConfig
from engine.simulation import Simulation
from engine.world_state import WorldState, RelationType
from engine.event_bus import EventBus, SimEvent, EventCategory, EventSeverity
from engine.war_simulator import WarSimulator
from engine.shadow_powers import ShadowPowerEngine
from engine.future_predictor import FuturePredictionEngine
from data.mass_loader import load_all_countries_mass, initialize_leaders
from data.leader_generator import CURRENT_LEADERS_2025
from llm.registry import get_provider

app = FastAPI(title="WORLD ORDER")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ═══════════════════════════════════════════════════════════════
# PERSISTENT GLOBAL STATE
# ═══════════════════════════════════════════════════════════════

_sim: Simulation | None = None
_ws_clients: list[WebSocket] = []
_turn_history: list[dict[str, Any]] = []


async def _broadcast(msg: dict[str, Any]) -> None:
    data = json.dumps(msg, default=str)
    dead: list[WebSocket] = []
    for ws in _ws_clients:
        try:
            await ws.send_text(data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _ws_clients.remove(ws)


def _ensure_sim(provider: str = "ollama", model: str = "qwen2.5:7b") -> Simulation:
    global _sim
    if _sim is None:
        config = SimulationConfig(
            start_year=2025, max_turns=100,
            llm_provider=provider, llm_model=model, seed=42,
        )
        llm = get_provider(provider, model=model)
        _sim = Simulation(config=config, llm=llm, use_advisors=False)
        _sim.setup()
    return _sim


# ═══════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.post("/api/simulation/start")
async def start_simulation(provider: str = "ollama", model: str = "qwen2.5:7b"):
    global _sim, _turn_history
    _sim = None
    _turn_history = []
    sim = _ensure_sim(provider, model)
    await _broadcast({"type": "sim_started", "year": sim.world.year, "countries": len(sim.world.countries)})
    return {"status": "ok", "year": sim.world.year, "countries": len(sim.world.countries)}


@app.post("/api/simulation/next-turn")
async def next_turn():
    sim = _ensure_sim()
    await _broadcast({"type": "turn_started", "turn": sim.world.turn})
    result = await sim.run_turn()
    _turn_history.append(result)
    await _broadcast({"type": "turn_complete", **result})
    return result


@app.get("/api/simulation/state")
async def get_sim_state():
    sim = _ensure_sim()
    return sim.get_state_snapshot()


@app.get("/api/countries")
async def get_countries():
    sim = _ensure_sim()
    result = []
    for c in sim.world.ranked_by_power():
        leader = sim.leader_system.current_leaders.get(c.code) if sim.leader_system else None
        result.append({
            "code": c.code, "name": c.name,
            "power": round(c.composite_power, 1),
            "gdp": round(c.economy.gdp_trillion, 2),
            "gdpGrowth": round(c.economy.gdp_growth, 1),
            "military": round(c.military.power_index, 2),
            "stability": round(c.domestic.stability, 2),
            "population": round(c.domestic.population_million, 1),
            "nuclear": c.military.nuclear,
            "techLevel": round(c.domestic.tech_level, 2),
            "democracy": round(c.domestic.democracy_index, 2),
            "inflation": round(c.economy.inflation, 1),
            "unemployment": round(c.economy.unemployment, 1),
            "leader": leader.name if leader else "Unknown",
            "leaderTraits": leader.traits if leader else [],
            "alliances": c.alliances,
            "relations": {k: v.value for k, v in c.relations.items()},
        })
    return result


@app.get("/api/war/{attacker}/{defender}")
async def simulate_war(attacker: str, defender: str):
    sim = _ensure_sim()
    a = sim.world.get(attacker.upper())
    d = sim.world.get(defender.upper())
    if not a or not d:
        return {"error": "Country not found"}

    att_allies = sim.war_sim.find_allies(attacker.upper(), defender.upper())
    def_allies = sim.war_sim.find_allies(defender.upper(), attacker.upper())
    att_ally_states = [sim.world.get(x) for x in att_allies if sim.world.get(x)]
    def_ally_states = [sim.world.get(x) for x in def_allies if sim.world.get(x)]
    att_power = sim.war_sim.calculate_combat_power(a, att_ally_states)
    def_power = sim.war_sim.calculate_combat_power(d, def_ally_states)
    ratio = att_power / max(def_power, 0.1)

    nuclear_risk = 0.0
    if a.military.nuclear and d.military.nuclear:
        nuclear_risk = 0.15
    elif a.military.nuclear or d.military.nuclear:
        nuclear_risk = 0.05

    probs = sim.war_sim._calculate_outcome_probabilities(ratio, nuclear_risk, a, d)
    profits = sim.shadow_powers.calculate_war_profit([attacker.upper(), defender.upper()], 0.7)
    att_suppliers = [s.name for s in sim.shadow_powers.get_arms_suppliers(attacker.upper())]
    def_suppliers = [s.name for s in sim.shadow_powers.get_arms_suppliers(defender.upper())]

    return {
        "attacker": {"code": a.code, "name": a.name, "power": att_power, "nuclear": a.military.nuclear,
                     "troops": a.military.active_personnel, "gdp": a.economy.gdp_trillion},
        "defender": {"code": d.code, "name": d.name, "power": def_power, "nuclear": d.military.nuclear,
                     "troops": d.military.active_personnel, "gdp": d.economy.gdp_trillion},
        "ratio": round(ratio, 2), "nuclearRisk": round(nuclear_risk, 3),
        "attackerAllies": att_allies, "defenderAllies": def_allies,
        "outcomes": probs, "profiteers": profits,
        "attackerSuppliers": att_suppliers, "defenderSuppliers": def_suppliers,
    }


@app.post("/api/war/start/{attacker}/{defender}")
async def start_war(attacker: str, defender: str, casus_belli: str = "territorial dispute"):
    sim = _ensure_sim()
    try:
        report = await sim.war_sim.start_war(attacker.upper(), defender.upper(), casus_belli)
        await _broadcast({"type": "war_started", "attacker": attacker.upper(), "defender": defender.upper()})
        return {"status": "ok", "war_id": f"{attacker.upper()}_vs_{defender.upper()}_{sim.world.turn}",
                "report": report.model_dump()}
    except ValueError as e:
        return {"error": str(e)}


@app.get("/api/predictions")
async def get_predictions(timeframe: int = 10, limit: int = 20):
    sim = _ensure_sim()
    if sim.predictor:
        preds = sim.predictor.generate_all_predictions(timeframe)
    else:
        preds = []
    return [
        {"id": p.id, "category": p.category.value, "title": p.title,
         "description": p.description, "probability": p.probability,
         "confidence": p.confidence, "impact": p.impact_severity,
         "countries": p.affected_countries, "triggers": p.triggers,
         "dominoEffects": p.domino_effects, "timeframe": p.timeframe_years}
        for p in preds[:limit]
    ]


@app.get("/api/shadows")
async def get_shadows():
    sim = _ensure_sim()
    sp = sim.shadow_powers
    return {
        "armsDealers": [
            {"name": d.name, "hq": d.headquarters, "revenue": d.annual_revenue_billion,
             "marketShare": d.market_share, "weapons": d.weapons_types[:5],
             "clients": d.export_destinations[:8], "influence": d.influence_score}
            for d in sp.arms_dealers
        ],
        "pmcs": [
            {"name": p.name, "patron": p.patron_state, "personnel": p.personnel_count,
             "combatXP": p.combat_experience, "conflicts": p.active_conflicts[:4],
             "warCrimes": p.war_crimes_allegations}
            for p in sp.pmcs
        ],
        "financials": [
            {"name": f.name, "hq": f.headquarters, "description": f.description,
             "influence": f.influence_score, "aum": f.assets_under_management_billion,
             "evasion": f.sanctions_evasion_capability}
            for f in sp.financials
        ],
        "energyCartels": [
            {"name": c.name, "production": c.daily_production_mboe,
             "priceControl": c.price_manipulation_power,
             "chokepoints": c.chokepoint_influence}
            for c in sp.energy_cartels
        ],
    }


@app.get("/api/active-wars")
async def get_active_wars():
    sim = _ensure_sim()
    return {
        wid: r.model_dump()
        for wid, r in sim.war_sim.active_wars.items()
    }


@app.get("/api/history")
async def get_turn_history():
    return _turn_history


@app.post("/api/crisis/inject")
async def inject_crisis(title: str = "Custom Crisis", description: str = "A major crisis erupts.",
                        target_countries: str = ""):
    sim = _ensure_sim()
    targets = [t.strip().upper() for t in target_countries.split(",") if t.strip()]
    event = await sim.crisis_gen.inject_custom(title=title, description=description, target_countries=targets)
    await _broadcast({"type": "crisis", "title": title})
    return {"status": "ok", "event": event.model_dump()}


@app.post("/api/leader/change/{country_code}")
async def force_leader_change(country_code: str, reason: str = "coup"):
    sim = _ensure_sim()
    code = country_code.upper()
    if sim.leader_system:
        trans = sim.leader_system._transition(code, sim.world.year, reason)
        country = sim.world.get(code)
        new_leader = sim.leader_system.get_leader(code)
        if country and new_leader:
            country.leader_id = new_leader.leader_id
            sim._rebuild_leader_agent(country)
        await _broadcast({"type": "leader_change", "country": code, "reason": reason})
        return {"status": "ok", **trans}
    return {"error": "No leader system"}


# ═══════════════════════════════════════════════════════════════
# WEBSOCKET
# ═══════════════════════════════════════════════════════════════

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    _ws_clients.append(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        if ws in _ws_clients:
            _ws_clients.remove(ws)


# ═══════════════════════════════════════════════════════════════
# SERVE CINEMATIC UI
# ═══════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = _Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
