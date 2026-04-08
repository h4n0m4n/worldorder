"""Prompt engineering — builds system & user prompts for leader agents."""

from __future__ import annotations

from typing import Any

from engine.world_state import CountryState
from engine.event_bus import SimEvent


DECISION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "inner_thoughts": {
            "type": "string",
            "description": "Leader's private reasoning (chain-of-thought)",
        },
        "public_statement": {
            "type": "string",
            "description": "What the leader says publicly (1-3 sentences)",
        },
        "actions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "diplomacy", "military", "economic", "intelligence",
                            "trade", "alliance", "sanction", "aid",
                            "domestic_policy", "propaganda", "negotiate",
                            "threaten", "concede", "stall", "no_action",
                        ],
                    },
                    "target": {"type": "string", "description": "Target country code or 'global'"},
                    "detail": {"type": "string", "description": "Specific action description"},
                    "intensity": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "How aggressive/strong (0=minimal, 1=maximum)",
                    },
                },
                "required": ["type", "target", "detail"],
            },
        },
        "mood": {
            "type": "string",
            "enum": ["confident", "anxious", "aggressive", "defensive", "opportunistic", "desperate"],
        },
    },
    "required": ["inner_thoughts", "public_statement", "actions", "mood"],
}


def build_leader_system_prompt(
    leader_profile: dict[str, Any],
    country: CountryState,
) -> str:
    p = leader_profile
    personality = p.get("personality", {})
    decision = p.get("decision_framework", {})
    worldview = p.get("worldview", {})

    traits = ", ".join(personality.get("traits", []))
    priorities = "\n".join(f"  - {pr}" for pr in decision.get("priorities", []))
    red_lines = "\n".join(f"  - {rl}" for rl in decision.get("red_lines", []))
    beliefs = "\n".join(f"  - {b}" for b in worldview.get("key_beliefs", []))

    return f"""You are {p['name']}, {p.get('title', 'Leader')} of {country.name}.

PERSONALITY: {traits}
IDEOLOGY: {personality.get('ideology', 'pragmatic')}
COMMUNICATION STYLE: {personality.get('communication_style', '')}
RISK TOLERANCE: {personality.get('risk_tolerance', 0.5)}/1.0

YOUR PRIORITIES (in order):
{priorities}

YOUR RED LINES (will escalate if crossed):
{red_lines}

YOUR CORE BELIEFS:
{beliefs}

NEGOTIATION STYLE: {decision.get('negotiation_style', '')}

YOUR COUNTRY'S CURRENT STATE:
- GDP: ${country.economy.gdp_trillion:.1f}T | Growth: {country.economy.gdp_growth:.1f}%
- Military Power: {country.military.power_index:.0%} | Nuclear: {country.military.nuclear}
- Stability: {country.domestic.stability:.0%} | Democracy: {country.domestic.democracy_index:.0%}
- Population: {country.domestic.population_million:.0f}M
- Alliances: {', '.join(country.alliances) or 'None'}
- Composite Power Score: {country.composite_power}/100

INSTRUCTIONS:
- Stay completely in character as {p['name']}.
- Think strategically based on your personality, priorities, and worldview.
- Consider your country's actual capabilities and limitations.
- Your decisions must be consistent with your known political behavior.
- Respond ONLY with the JSON decision object. No other text."""


def build_turn_prompt(
    turn: int,
    year: int,
    recent_events: list[SimEvent],
    world_summary: str,
    memory_context: str = "",
) -> str:
    events_text = "\n".join(f"  - {e}" for e in recent_events) if recent_events else "  (no major events)"

    prompt = f"""YEAR: {year} | TURN: {turn}

RECENT EVENTS:
{events_text}

WORLD SITUATION:
{world_summary}
"""
    if memory_context:
        prompt += f"\nYOUR MEMORY OF PAST EVENTS:\n{memory_context}\n"

    prompt += "\nWhat is your response? Analyze the situation and decide your actions."
    return prompt


def build_world_summary(countries: list[CountryState]) -> str:
    lines = ["GLOBAL POWER RANKINGS:"]
    for i, c in enumerate(sorted(countries, key=lambda x: x.composite_power, reverse=True), 1):
        status = []
        if c.economy.gdp_growth < 0:
            status.append("RECESSION")
        if c.economy.inflation > 10:
            status.append("HIGH INFLATION")
        if c.domestic.stability < 0.4:
            status.append("UNSTABLE")
        wars = [k for k, v in c.relations.items() if v.value == "war"]
        if wars:
            status.append(f"AT WAR with {', '.join(wars)}")
        status_str = f" [{', '.join(status)}]" if status else ""
        lines.append(
            f"  {i}. {c.name} ({c.code}) — Power: {c.composite_power:.1f}/100 | "
            f"GDP: ${c.economy.gdp_trillion:.1f}T | Mil: {c.military.power_index:.0%}{status_str}"
        )

    lines.append("\nDIPLOMATIC TENSIONS:")
    for c in countries:
        hostile = [
            f"{k} ({v.value})"
            for k, v in c.relations.items()
            if v.value in ("hostile", "war", "tense")
        ]
        if hostile:
            lines.append(f"  {c.code}: {', '.join(hostile)}")

    return "\n".join(lines)
