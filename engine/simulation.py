"""Simulation orchestrator — ties all engine components together."""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Awaitable

from engine.config import SimulationConfig, GameMode
from engine.world_state import WorldState, CountryState
from engine.event_bus import EventBus, SimEvent, EventCategory, EventSeverity
from engine.time_engine import TimeEngine
from engine.crisis import CrisisGenerator
from data.loader import load_all_countries, load_all_leader_profiles
from llm.base import LLMProvider
from llm.prompt_builder import (
    build_leader_system_prompt,
    build_turn_prompt,
    build_world_summary,
    DECISION_SCHEMA,
)


TurnCallback = Callable[[int, int, list[SimEvent], dict[str, Any]], Awaitable[None]]


class Simulation:
    """Main simulation loop."""

    def __init__(
        self,
        config: SimulationConfig,
        llm: LLMProvider,
        on_turn: TurnCallback | None = None,
    ) -> None:
        self.config = config
        self.llm = llm
        self.on_turn = on_turn

        self.world = WorldState()
        self.event_bus = EventBus()
        self.time_engine = TimeEngine(config, self.world, self.event_bus)
        self.crisis_gen = CrisisGenerator(
            self.world, self.event_bus, rng_seed=config.seed
        )

        self.leader_profiles: dict[str, dict[str, Any]] = {}
        self.decisions_log: list[dict[str, Any]] = []

    def setup(self) -> None:
        """Load countries and leader profiles."""
        countries = load_all_countries()
        for c in countries:
            self.world.add_country(c)

        self.leader_profiles = load_all_leader_profiles()
        for lid, profile in self.leader_profiles.items():
            country_code = profile.get("country")
            country = self.world.get(country_code)
            if country:
                country.leader_id = lid

    async def run_turn(self) -> dict[str, Any]:
        """Execute a single simulation turn."""
        turn = self.world.turn
        year = self.world.year

        crises = await self.crisis_gen.roll_crises()

        recent_events = self.event_bus.history(last_n=10)
        world_summary = build_world_summary(self.world.all_countries())

        turn_decisions: dict[str, Any] = {}

        for country in self.world.all_countries():
            if not country.leader_id:
                continue

            if (
                self.config.game_mode == GameMode.LEADER
                and country.code == self.config.player_country
            ):
                continue  # player decides via CLI

            profile = self.leader_profiles.get(country.leader_id)
            if not profile:
                continue

            system_prompt = build_leader_system_prompt(profile, country)
            turn_prompt = build_turn_prompt(turn, year, recent_events, world_summary)

            try:
                decision = await self.llm.generate_structured(
                    prompt=turn_prompt,
                    schema=DECISION_SCHEMA,
                    system=system_prompt,
                )
            except Exception as e:
                decision = {
                    "inner_thoughts": f"[AI Error: {e}]",
                    "public_statement": "No comment at this time.",
                    "actions": [{"type": "no_action", "target": "global", "detail": "Waiting"}],
                    "mood": "cautious",
                }

            turn_decisions[country.code] = decision

            for action in decision.get("actions", []):
                await self.event_bus.publish(SimEvent(
                    turn=turn,
                    year=year,
                    category=self._action_to_category(action.get("type", "diplomacy")),
                    severity=self._intensity_to_severity(action.get("intensity", 0.5)),
                    title=f"{country.name}: {action.get('type', 'action').replace('_', ' ').title()}",
                    description=action.get("detail", ""),
                    source_country=country.code,
                    target_countries=[action["target"]] if action.get("target") != "global" else [],
                ))

        self.decisions_log.append({
            "turn": turn,
            "year": year,
            "decisions": turn_decisions,
            "crises": [c.model_dump() for c in crises],
        })

        if self.on_turn:
            await self.on_turn(turn, year, recent_events, turn_decisions)

        alive = await self.time_engine.tick()
        return {"turn": turn, "year": year, "decisions": turn_decisions, "continue": alive}

    async def run(self, turns: int | None = None) -> None:
        """Run the full simulation loop."""
        max_turns = turns or self.config.max_turns
        for _ in range(max_turns):
            result = await self.run_turn()
            if not result["continue"]:
                break

    @staticmethod
    def _action_to_category(action_type: str) -> EventCategory:
        mapping = {
            "diplomacy": EventCategory.DIPLOMATIC,
            "military": EventCategory.MILITARY,
            "economic": EventCategory.ECONOMIC,
            "intelligence": EventCategory.INTELLIGENCE,
            "trade": EventCategory.ECONOMIC,
            "alliance": EventCategory.DIPLOMATIC,
            "sanction": EventCategory.ECONOMIC,
            "aid": EventCategory.DIPLOMATIC,
            "domestic_policy": EventCategory.POLITICAL,
            "propaganda": EventCategory.POLITICAL,
            "negotiate": EventCategory.DIPLOMATIC,
            "threaten": EventCategory.MILITARY,
            "concede": EventCategory.DIPLOMATIC,
            "stall": EventCategory.DIPLOMATIC,
        }
        return mapping.get(action_type, EventCategory.POLITICAL)

    @staticmethod
    def _intensity_to_severity(intensity: float) -> EventSeverity:
        if intensity >= 0.8:
            return EventSeverity.CRITICAL
        if intensity >= 0.5:
            return EventSeverity.HIGH
        if intensity >= 0.2:
            return EventSeverity.MEDIUM
        return EventSeverity.LOW
