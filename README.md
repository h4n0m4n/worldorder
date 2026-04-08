<div align="center">

# 🌍 WORLD ORDER

### AI-Powered Civilization & Geopolitical Simulation Engine

**Real leaders. Real personalities. Simulated futures.**

*History doesn't repeat itself, but it rhymes. Now you can hear the next verse.*

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](https://nextjs.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Stars](https://img.shields.io/github/stars/h4n0m4n/worldorder?style=social)](https://github.com/h4n0m4n/worldorder)

---

**What if WW3 started tomorrow?** · **Can AI prevent wars?** · **Ottoman Empire in 2025?**

WORLD ORDER simulates global geopolitics using AI agents that think, negotiate, threaten, and make decisions like real world leaders — from ancient civilizations to the year 2100.

</div>

---

## ⚡ Quick Start

```bash
# Clone
git clone https://github.com/h4n0m4n/worldorder.git
cd worldorder

# Install
pip install -e .

# Run (requires Ollama running locally)
worldorder start --turns 20

# Or use free cloud API (no local GPU needed)
worldorder start --provider groq --model llama-3.1-8b-instant
```

## 🎮 What Is This?

WORLD ORDER is a **multi-agent geopolitical simulation engine** where:

- **21 nations** are modeled with real economic, military, and political data
- **AI agents** embody real world leaders (Putin, Xi, Erdogan, Biden...) with their actual personalities, ideologies, and decision-making patterns
- **Civilization DNA** — each nation carries deep cultural/historical identity that persists across centuries
- **Advisor panels** — each leader has military, economic, intelligence, diplomatic, and domestic advisors
- **Memory systems** — leaders remember past events, hold grudges, and form alliances
- **Crisis engine** — random or custom crises (pandemics, oil shocks, nuclear threats) inject chaos
- **"What If?" mode** — inject any scenario and watch the world react

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   UI LAYER                       │
│  ┌──────────────┐  ┌────────────────────────┐   │
│  │  CLI (Rich)   │  │  Web (Next.js + React) │   │
│  └──────────────┘  └────────────────────────┘   │
├─────────────────────────────────────────────────┤
│                  API (FastAPI)                    │
├─────────────────────────────────────────────────┤
│               AI AGENT LAYER                     │
│  ┌────────┐ ┌──────────┐ ┌───────────────────┐  │
│  │Leaders │ │ Advisors │ │ Civilization DNA  │  │
│  │(LLM)   │ │ (5 each) │ │ (Cultural Memory) │  │
│  └────────┘ └──────────┘ └───────────────────┘  │
├─────────────────────────────────────────────────┤
│              CORE ENGINE (Python)                 │
│  ┌────────────┐ ┌──────┐ ┌────────┐ ┌───────┐  │
│  │World State │ │Time  │ │Event   │ │Crisis │  │
│  │Manager     │ │Engine│ │Bus     │ │Gen    │  │
│  └────────────┘ └──────┘ └────────┘ └───────┘  │
├─────────────────────────────────────────────────┤
│            LLM LAYER (Pluggable)                 │
│  Ollama │ Groq │ OpenRouter │ OpenAI │ Any LLM  │
└─────────────────────────────────────────────────┘
```

## 🌐 21 Nations Modeled

| Rank | Country | Power | Nuclear | Key Feature |
|------|---------|-------|---------|-------------|
| 1 | 🇺🇸 United States | 85.6 | ✅ | Global hegemon, tech leader |
| 2 | 🇨🇳 China | 80.2 | ✅ | Rising superpower, manufacturing giant |
| 3 | 🇪🇺 European Union | 65.2 | ✅ | Regulatory superpower, peace project |
| 4 | 🇮🇳 India | 51.9 | ✅ | Demographic dividend, tech hub |
| 5 | 🇯🇵 Japan | 45.5 | ❌ | Tech innovator, aging society |
| 6 | 🇷🇺 Russia | 45.4 | ✅ | Energy superpower, military power |
| 7 | 🇬🇧 United Kingdom | 43.0 | ✅ | Intelligence hub, financial center |
| 8 | 🇫🇷 France | 41.1 | ✅ | Nuclear power, EU co-leader |
| 9 | 🇮🇱 Israel | 40.2 | ✅ | Tech powerhouse, cyber leader |
| 10 | 🇩🇪 Germany | 39.9 | ❌ | Economic engine of Europe |
| 11 | 🇰🇷 South Korea | 39.9 | ❌ | K-wave, semiconductor leader |
| 12 | 🇦🇺 Australia | 34.7 | ❌ | Resource exporter, AUKUS member |
| 13 | 🇹🇷 Turkey | 33.9 | ❌ | NATO's eastern flank, bridge between worlds |
| 14 | 🇸🇦 Saudi Arabia | 29.6 | ❌ | Oil kingdom, Vision 2030 |
| 15 | 🇧🇷 Brazil | 29.0 | ❌ | South American giant, Amazon guardian |
| 16 | 🇮🇷 Iran | 27.6 | ❌ | Resistance axis, nuclear threshold |
| 17 | 🇵🇰 Pakistan | 25.0 | ✅ | Nuclear state, China corridor |
| 18 | 🇺🇦 Ukraine | 24.9 | ❌ | Frontline of democracy |
| 19 | 🇪🇬 Egypt | 24.2 | ❌ | Suez controller, Arab anchor |
| 20 | 🇰🇵 North Korea | 23.7 | ✅ | Nuclear hermit kingdom |
| 21 | 🇳🇬 Nigeria | 16.6 | ❌ | Africa's most populous nation |

## 🧠 How Leaders Think

Each AI leader agent has:

```yaml
Putin:
  personality: [strategic, calculating, risk-taker, KGB-mentality]
  priorities: [regime_survival, great_power_status, NATO_containment]
  red_lines: [NATO expansion to Ukraine, regime change attempts]
  negotiation_style: "escalate-to-deescalate, create facts on the ground"
  memory: remembers past betrayals, holds grudges
  advisors: military (hawkish), economic, intelligence (paranoid)
```

Leaders don't just respond — they **think strategically**, consult advisors, recall past events, and act according to their real-world personality patterns.

## 🎯 Pre-Built Scenarios

| Scenario | Description |
|----------|-------------|
| **Taiwan Strait Crisis** | China moves on Taiwan. How does the world respond? |
| **World War III** | NATO-Russia escalation spirals into global conflict |
| **Global Oil Embargo** | OPEC+ halts exports. Energy crisis engulfs the world |
| **Ottoman Empire in 2025** | What if the Ottoman Empire never fell? |
| **AI Singularity Race** | Nations race to achieve artificial superintelligence |

## 🖥️ CLI Interface

```bash
# Start with defaults
worldorder start

# Custom scenario
worldorder start --era contemporary --start-year 2025 --turns 50

# Play as a country
worldorder start --mode leader --player-country TR

# Use different LLM
worldorder start --provider groq --model llama-3.1-8b-instant

# View world map
worldorder map

# Browse history
worldorder history

# List scenarios
worldorder scenarios

# Fetch live news
worldorder news
```

## 🌐 Web Interface

```bash
# Start the API server
cd worldorder
uvicorn api.server:app --reload

# In another terminal, start the web UI
cd web
npm run dev
```

Then open http://localhost:3000

## 🔌 LLM Providers

| Provider | Cost | Speed | Setup |
|----------|------|-------|-------|
| **Ollama** (default) | Free | Local | `ollama pull llama3.1` |
| **Groq** | Free tier | Very fast | Set `GROQ_API_KEY` |
| **OpenRouter** | Free models | Fast | Set `OPENROUTER_API_KEY` |
| **OpenAI** | Paid | Fast | Set `OPENAI_API_KEY` |

## 🐳 Docker

```bash
docker-compose up
# API: http://localhost:8000
# Web: http://localhost:3000
```

## 📁 Project Structure

```
worldorder/
├── engine/          # Core simulation engine
│   ├── world_state.py    # Nation state management
│   ├── time_engine.py    # Simulation clock
│   ├── event_bus.py      # Event system
│   ├── crisis.py         # Crisis generator
│   └── simulation.py     # Main orchestrator
├── agents/          # AI agent layer
│   ├── leader_agent.py   # Leader AI with memory
│   ├── advisor_agent.py  # Specialized advisors
│   ├── civilization_dna.py # Cultural DNA
│   ├── memory.py         # Episodic/semantic memory
│   └── decision.py       # Decision framework
├── llm/             # Pluggable LLM backends
│   ├── ollama.py         # Local (free)
│   ├── groq.py           # Cloud (free tier)
│   ├── openrouter.py     # Multi-model
│   └── openai_provider.py # OpenAI
├── data/            # Profiles & historical data
│   ├── profiles/         # 21 country + leader YAML profiles
│   └── historical/       # Events, wars, treaties
├── cli/             # Terminal interface (Rich)
├── api/             # FastAPI REST + WebSocket
├── web/             # Next.js web interface
└── docker-compose.yml
```

## 🤝 Contributing

This is an open-source project. Contributions welcome:

- **Add countries** — Create YAML profiles in `data/profiles/`
- **Add scenarios** — Extend `data/historical/events.json`
- **Add LLM providers** — Implement `LLMProvider` interface
- **Improve leader personalities** — Make them more accurate
- **Build visualizations** — Charts, maps, timelines

## 📜 License

MIT License — do whatever you want with it.

---

<div align="center">

**Built with obsession by [h4n0m4n](https://github.com/h4n0m4n)**

*"The supreme art of war is to subdue the enemy without fighting."* — Sun Tzu

⭐ Star this repo if you want to simulate the apocalypse responsibly.

</div>
