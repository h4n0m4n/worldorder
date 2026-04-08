"""FastAPI server — bridges the simulation engine to the web UI."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from engine.config import SimulationConfig, Era, TimeScale, GameMode
from engine.simulation import Simulation
from engine.event_bus import SimEvent
from data.loader import load_all_countries, load_all_leader_profiles
from llm.registry import get_provider, available_providers

app = FastAPI(
    title="WORLD ORDER API",
    description="AI-Powered Geopolitical Simulation Engine",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global simulation state
_simulation: Simulation | None = None
_ws_clients: list[WebSocket] = []


class SimulationRequest(BaseModel):
    era: str = "contemporary"
    start_year: int = 2025
    end_year: int = 2100
    max_turns: int = 20
    time_scale: str = "year"
    game_mode: str = "god"
    player_country: str | None = None
    llm_provider: str = "ollama"
    llm_model: str = "llama3.1"
    seed: int | None = None


class CrisisRequest(BaseModel):
    title: str
    description: str
    category: str = "crisis"
    severity: str = "critical"
    target_countries: list[str] = []


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": "WORLD ORDER", "version": "0.1.0", "status": "operational"}


@app.get("/providers")
async def list_providers() -> dict[str, list[str]]:
    return {"providers": available_providers()}


@app.get("/providers/{name}/health")
async def check_provider(name: str) -> dict[str, Any]:
    try:
        llm = get_provider(name)
        ok = await llm.health_check()
        return {"provider": name, "healthy": ok}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/countries")
async def list_countries() -> list[dict[str, Any]]:
    countries = load_all_countries()
    return [
        {
            "code": c.code,
            "name": c.name,
            "composite_power": c.composite_power,
            "gdp_trillion": c.economy.gdp_trillion,
            "military_power": c.military.power_index,
            "stability": c.domestic.stability,
            "population_million": c.domestic.population_million,
            "nuclear": c.military.nuclear,
            "alliances": c.alliances,
        }
        for c in sorted(countries, key=lambda x: x.composite_power, reverse=True)
    ]


@app.get("/leaders")
async def list_leaders() -> list[dict[str, Any]]:
    leaders = load_all_leader_profiles()
    return [
        {
            "id": lid,
            "name": profile.get("name"),
            "country": profile.get("country"),
            "title": profile.get("title"),
            "ideology": profile.get("personality", {}).get("ideology", ""),
            "risk_tolerance": profile.get("personality", {}).get("risk_tolerance", 0.5),
            "traits": profile.get("personality", {}).get("traits", []),
        }
        for lid, profile in leaders.items()
    ]


@app.get("/scenarios")
async def list_scenarios() -> list[dict[str, Any]]:
    from engine.config import DATA_DIR
    events_path = DATA_DIR / "historical" / "events.json"
    with open(events_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("scenario_templates", [])


@app.get("/history")
async def get_history() -> dict[str, Any]:
    from engine.config import DATA_DIR
    events_path = DATA_DIR / "historical" / "events.json"
    with open(events_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("eras", {})


@app.post("/simulation/create")
async def create_simulation(req: SimulationRequest) -> dict[str, Any]:
    global _simulation

    config = SimulationConfig(
        era=Era(req.era),
        start_year=req.start_year,
        end_year=req.end_year,
        max_turns=req.max_turns,
        time_scale=TimeScale(req.time_scale),
        game_mode=GameMode(req.game_mode),
        player_country=req.player_country,
        llm_provider=req.llm_provider,
        llm_model=req.llm_model,
        seed=req.seed,
    )

    llm = get_provider(req.llm_provider, model=req.llm_model)

    async def on_turn(turn: int, year: int, events: list[SimEvent], decisions: dict[str, Any]) -> None:
        payload = json.dumps({
            "type": "turn_update",
            "turn": turn,
            "year": year,
            "events": [e.model_dump(mode="json") for e in events[-10:]],
            "decisions": decisions,
        }, default=str)
        for ws in _ws_clients[:]:
            try:
                await ws.send_text(payload)
            except Exception:
                _ws_clients.remove(ws)

    _simulation = Simulation(config=config, llm=llm, on_turn=on_turn)
    _simulation.setup()

    return {
        "status": "created",
        "countries": len(_simulation.world.countries),
        "leaders": len(_simulation.leader_profiles),
        "config": config.model_dump(),
    }


@app.post("/simulation/turn")
async def run_turn() -> dict[str, Any]:
    if not _simulation:
        raise HTTPException(status_code=400, detail="No simulation created. POST /simulation/create first.")
    result = await _simulation.run_turn()
    world = _simulation.world
    return {
        "turn": result["turn"],
        "year": result["year"],
        "continue": result["continue"],
        "decisions": result["decisions"],
        "power_rankings": [
            {"code": c.code, "name": c.name, "power": c.composite_power}
            for c in world.ranked_by_power()
        ],
    }


@app.get("/simulation/state")
async def get_state() -> dict[str, Any]:
    if not _simulation:
        raise HTTPException(status_code=400, detail="No simulation running.")
    world = _simulation.world
    return {
        "turn": world.turn,
        "year": world.year,
        "countries": [
            {
                "code": c.code,
                "name": c.name,
                "composite_power": c.composite_power,
                "gdp_trillion": c.economy.gdp_trillion,
                "gdp_growth": c.economy.gdp_growth,
                "inflation": c.economy.inflation,
                "military_power": c.military.power_index,
                "stability": c.domestic.stability,
                "population_million": c.domestic.population_million,
                "nuclear": c.military.nuclear,
                "alliances": c.alliances,
                "relations": {k: v.value for k, v in c.relations.items()},
            }
            for c in world.ranked_by_power()
        ],
        "total_events": _simulation.event_bus.total_events,
    }


@app.post("/simulation/crisis")
async def inject_crisis(req: CrisisRequest) -> dict[str, Any]:
    if not _simulation:
        raise HTTPException(status_code=400, detail="No simulation running.")
    event = await _simulation.crisis_gen.inject_custom(
        title=req.title,
        description=req.description,
        target_countries=req.target_countries,
    )
    return {"status": "injected", "event": event.model_dump(mode="json")}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
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


def start_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
