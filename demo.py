"""WORLD ORDER — Full demo with live AI decisions."""

import asyncio
from engine.config import SimulationConfig
from engine.simulation import Simulation
from llm.registry import get_provider

async def main():
    print()
    print("=" * 70)
    print("  WORLD ORDER — AI-Powered Geopolitical Simulation Engine")
    print("  Live Demo with Ollama / qwen2.5:7b")
    print("=" * 70)
    print()

    config = SimulationConfig(
        start_year=2025,
        max_turns=1,
        llm_provider="ollama",
        llm_model="qwen2.5:7b",
        seed=42,
    )
    llm = get_provider("ollama", model="qwen2.5:7b")

    sim = Simulation(config=config, llm=llm)
    sim.setup()

    print(f"[LOADED] {len(sim.world.countries)} countries")
    print(f"[LOADED] {len(sim.leader_system.current_leaders)} leaders")
    print(f"[LOADED] {len(sim.shadow_powers.arms_dealers)} arms dealers")
    print(f"[LOADED] {len(sim.shadow_powers.pmcs)} PMCs")
    print(f"[LOADED] {len(sim.shadow_powers.financials)} financial networks")
    print(f"[LOADED] {len(sim.shadow_powers.energy_cartels)} energy cartels")
    print()

    print("=" * 70)
    print("  TOP 15 WORLD POWERS")
    print("=" * 70)
    for i, c in enumerate(sim.world.ranked_by_power()[:15], 1):
        leader = sim.leader_system.current_leaders.get(c.code)
        lname = leader.name if leader else "?"
        nuke = " [NUCLEAR]" if c.military.nuclear else ""
        stab = int(c.domestic.stability * 100)
        bar = "#" * (stab // 10) + "." * (10 - stab // 10)
        print(f"  {i:2d}. {c.code} {c.name:28s} Power={c.composite_power:5.1f}  GDP=${c.economy.gdp_trillion:.1f}T  Stab=[{bar}]{stab}%  {lname}{nuke}")
    print()

    # Run Turn 1
    print("=" * 70)
    print("  TURN 1 — AI leaders making decisions via Ollama...")
    print("  (each leader thinks, consults advisors, then acts)")
    print("=" * 70)
    print()

    result = await sim.run_turn()
    year = result["year"]
    decisions = result["decisions"]

    print(f"  Year: {year} | Decisions from {len(decisions)} leaders")
    print()

    for code, dec in decisions.items():
        mood = dec.get("mood", "?")
        statement = dec.get("public_statement", "...")
        thoughts = dec.get("inner_thoughts", "")
        actions = dec.get("actions", [])

        print(f"  --- {code} [{mood.upper()}] ---")
        print(f'  Statement: "{statement[:150]}"')
        if thoughts:
            print(f"  Thinking:  {thoughts[:150]}")
        for a in actions[:3]:
            atype = a.get("type", "?").upper()
            target = a.get("target", "?")
            detail = a.get("detail", "")[:100]
            intensity = a.get("intensity", 0.5)
            bar = "#" * int(intensity * 10) + "." * (10 - int(intensity * 10))
            print(f"    [{bar}] {atype} -> {target}: {detail}")
        print()

    # Events
    print("=" * 70)
    print("  EVENTS THIS TURN")
    print("=" * 70)
    for e in sim.event_bus.history(last_n=15):
        sev = e.severity.value.upper()
        src = f" ({e.source_country})" if e.source_country else ""
        print(f"  [{sev:8s}] {e.title}{src}")
        if e.description:
            print(f"             {e.description[:120]}")
    print()

    # Predictions
    print("=" * 70)
    print("  TOP 5 FUTURE PREDICTIONS")
    print("=" * 70)
    preds = sim.predictor.get_top_risks(5)
    for i, p in enumerate(preds, 1):
        prob = p.probability * 100
        impact = int(p.impact_severity * 10)
        bar = "#" * impact + "." * (10 - impact)
        print(f"  {i}. [{p.category.value.upper():20s}] {p.title}")
        print(f"     Probability: {prob:.1f}% | Impact: [{bar}] | Countries: {', '.join(p.affected_countries[:5])}")
    print()

    print("=" * 70)
    print("  DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
