# WORLD ORDER

**AI-Powered Geopolitical Simulation Engine**

A real-time geopolitical simulation where AI-controlled world leaders make strategic decisions, wars unfold across turns, shadow powers profit from chaos, and you control the fate of nations — all visualized on an interactive 3D globe.

## What Is This?

WORLD ORDER simulates the entire world — 176 nations, 48 real leaders (Putin, Xi, Biden, Erdogan...), arms dealers, PMCs, energy cartels — all driven by AI. Each turn, leaders analyze the world situation and make decisions: diplomacy, military action, trade, sanctions. Wars start, alliances shift, economies crash, coups happen.

You watch it unfold on a cinematic 3D globe. Or you intervene: start wars, inject crises, force coups, form alliances.

## Features

### Simulation Engine
- **176 countries** with real economic, military, demographic data
- **48 hand-crafted leader profiles** (personality, ideology, risk tolerance)
- **AI-driven decisions** via local LLM (Ollama) — each leader thinks, consults advisors, then acts
- **Multi-turn wars** that progress through phases (mobilization → strike → ground → attrition → outcome)
- **Shadow powers** — arms dealers (Lockheed, BAE, Rosoboronexport), PMCs (Wagner, Academi), financial networks, energy cartels (OPEC+, Gazprom)
- **Dynamic leader transitions** — elections, coups, revolutions, deaths
- **Crisis system** — random events (pandemics, oil shocks, cyber attacks) + manual injection
- **Future predictions** — AI-generated threat analysis with probability scores

### 3D Cinematic UI
- **Three.js globe** with NASA Blue Marble texture, atmosphere glow, starfield
- **Country markers** sized by power, colored by status (war/unstable/nuclear)
- **War arcs** — red pulsing lines between warring nations
- **Hover tooltips** with country stats
- **Click interactions** — select countries, view intel, simulate wars
- **Cinematic turn transitions** — full-screen year animation + leader decision carousel
- **Particle explosions** for war effects
- **HUD overlay** — year counter, mini-stats, event ticker, active war badges

### Player Controls
- **Next Turn** — advance simulation, watch AI leaders decide
- **Declare War** — select two countries, see analysis, launch war
- **Inject Crisis** — custom crisis events that affect the world
- **Force Coup** — overthrow any leader
- **Form Alliance** — create bilateral alliances
- **Apply Sanctions** — economic warfare
- **Trade Deals** — boost economies between nations
- **Intel Mode** — view shadow powers, predictions, financial networks

## Quick Start

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.ai/) with a model installed

### Install & Run

```bash
# Clone
git clone https://github.com/h4n0m4n/worldorder.git
cd worldorder

# Install dependencies
pip install pydantic pyyaml httpx rich textual click fastapi uvicorn

# Install an LLM model
ollama pull qwen2.5:7b

# Run
python app.py
```

Open `http://127.0.0.1:8000` in your browser.

### First Steps
1. Click "CLICK TO BEGIN" on the intro screen
2. Click **NEXT TURN** — watch AI leaders make decisions
3. Click any country on the globe — see detailed intel
4. Click two countries — war simulation appears
5. Hit **INTEL** — see shadow powers and threat predictions
6. Hit **CRISIS** — inject a custom crisis

## Architecture

```
worldorder/
├── app.py                    # FastAPI server + API endpoints
├── static/index.html         # Cinematic 3D UI (Three.js)
├── engine/
│   ├── simulation.py         # Unified simulation loop
│   ├── war_simulator.py      # Lanchester combat model
│   ├── shadow_powers.py      # Arms dealers, PMCs, cartels
│   ├── future_predictor.py   # Threat prediction engine
│   ├── world_state.py        # Country state management
│   ├── event_bus.py          # Event pub/sub system
│   ├── time_engine.py        # Turn/year progression
│   ├── crisis.py             # Crisis generation
│   └── config.py             # Simulation configuration
├── agents/
│   ├── leader_agent.py       # AI leader with memory + advisors
│   ├── advisor_agent.py      # 5-role advisor panel
│   ├── memory.py             # Episodic/semantic memory
│   ├── decision.py           # Structured decision framework
│   └── civilization_dna.py   # National cultural identity
├── llm/
│   ├── ollama.py             # Ollama provider
│   ├── prompt_builder.py     # Leader/turn prompt engineering
│   └── registry.py           # LLM provider registry
├── data/
│   ├── world_database.py     # 176 countries raw data
│   ├── leader_generator.py   # 48 real leaders + dynamic system
│   └── mass_loader.py        # Country initialization
└── cli/
    ├── app.py                # CLI commands
    └── tui.py                # Terminal UI (Textual)
```

## Simulation Loop

Each turn executes this pipeline:

```
1. Leader transitions (elections, coups, deaths)
2. Random crises (oil shocks, pandemics, cyber attacks)
3. Advance active wars (phase progression, casualties)
4. Shadow powers tick (arms profits, PMC deployments)
5. AI leader decisions (memory + advisors + LLM)
6. Process actions (start wars, publish events)
7. Economic/population tick
8. Update predictions
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/simulation/start` | Start/reset simulation |
| POST | `/api/simulation/next-turn` | Advance one turn |
| GET | `/api/simulation/state` | Full state snapshot |
| GET | `/api/countries` | All 176 countries ranked |
| GET | `/api/war/{a}/{b}` | War scenario analysis |
| POST | `/api/war/start/{a}/{b}` | Start real war |
| GET | `/api/predictions` | Threat predictions |
| GET | `/api/shadows` | Shadow powers data |
| GET | `/api/active-wars` | Active conflicts |
| POST | `/api/crisis/inject` | Inject custom crisis |
| POST | `/api/leader/change/{code}` | Force leader change |
| POST | `/api/alliance/{a}/{b}` | Form/dissolve alliance |
| POST | `/api/sanction/{s}/{t}` | Apply sanctions |
| POST | `/api/trade/{a}/{b}` | Trade deal |
| WS | `/ws` | Live event stream |

## LLM Providers

WORLD ORDER supports multiple LLM backends:

| Provider | Model | Speed | Quality |
|----------|-------|-------|---------|
| Ollama | qwen2.5:7b | Fast | Good |
| Ollama | llama3.1:8b | Fast | Good |
| Groq | mixtral-8x7b | Very Fast | Great |
| OpenRouter | Any model | Varies | Varies |

## License

MIT
