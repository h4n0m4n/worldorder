"""Simulation orchestrator — ties all engine components together.

Unified loop: leader transitions → crises → advance wars → shadow tick →
AI leader decisions (via LeaderAgent) → process actions → time tick → predictions.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Awaitable

from engine.config import SimulationConfig, GameMode
from engine.world_state import WorldState, CountryState, RelationType
from engine.event_bus import EventBus, SimEvent, EventCategory, EventSeverity
from engine.time_engine import TimeEngine
from engine.crisis import CrisisGenerator
from data.loader import load_all_countries, load_all_leader_profiles
from data.mass_loader import load_all_countries_mass, initialize_leaders
from data.leader_generator import DynamicLeaderSystem
from llm.base import LLMProvider
from llm.prompt_builder import (
    build_leader_system_prompt,
    build_turn_prompt,
    build_world_summary,
    DECISION_SCHEMA,
)


TurnCallback = Callable[[int, int, list[SimEvent], dict[str, Any]], Awaitable[None]]


class Simulation:
    """Main simulation loop with fully integrated subsystems."""

    def __init__(
        self,
        config: SimulationConfig,
        llm: LLMProvider,
        on_turn: TurnCallback | None = None,
        use_advisors: bool = True,
    ) -> None:
        self.config = config
        self.llm = llm
        self.on_turn = on_turn
        self.use_advisors = use_advisors

        self.world = WorldState()
        self.event_bus = EventBus()
        self.time_engine = TimeEngine(config, self.world, self.event_bus)
        self.crisis_gen = CrisisGenerator(
            self.world, self.event_bus, rng_seed=config.seed
        )

        self.leader_profiles: dict[str, dict[str, Any]] = {}
        self.leader_system: DynamicLeaderSystem | None = None
        self.decisions_log: list[dict[str, Any]] = []

        from engine.shadow_powers import ShadowPowerEngine
        from engine.war_simulator import WarSimulator
        from engine.future_predictor import FuturePredictionEngine

        self.shadow_powers = ShadowPowerEngine(rng_seed=config.seed)
        self.war_sim = WarSimulator(self.world, self.event_bus, rng_seed=config.seed)
        self.predictor: FuturePredictionEngine | None = None

        # LeaderAgent instances keyed by country code
        self._leader_agents: dict[str, Any] = {}

    # ── setup ──────────────────────────────────────────────────

    def setup(self) -> None:
        """Load all 176 countries, leaders, and initialize subsystems."""
        countries = load_all_countries_mass()
        for c in countries:
            self.world.add_country(c)

        self.leader_system = initialize_leaders(
            countries, year=self.config.start_year, rng_seed=self.config.seed
        )

        self.leader_profiles = load_all_leader_profiles()

        from engine.future_predictor import FuturePredictionEngine
        self.predictor = FuturePredictionEngine(self.world, rng_seed=self.config.seed)

        self._init_leader_agents()

    def _init_leader_agents(self) -> None:
        """Create LeaderAgent instances for top countries."""
        from agents.leader_agent import LeaderAgent
        from agents.civilization_dna import CivilizationDNA

        top_countries = self.world.ranked_by_power()[:20]
        for country in top_countries:
            profile = self._resolve_leader_profile(country)
            if not profile:
                continue
            agent = LeaderAgent(
                leader_profile=profile,
                country=country,
                llm=self.llm,
                use_advisors=self.use_advisors,
                use_vector_memory=False,
            )
            self._leader_agents[country.code] = agent

    def _resolve_leader_profile(self, country: CountryState) -> dict[str, Any] | None:
        """Build a leader profile dict from YAML or DynamicLeaderSystem."""
        if country.leader_id:
            profile = self.leader_profiles.get(country.leader_id)
            if profile:
                return profile

        if self.leader_system:
            leader_term = self.leader_system.get_leader(country.code)
            if leader_term:
                return {
                    "id": leader_term.leader_id,
                    "name": leader_term.name,
                    "country": country.code,
                    "title": leader_term.title,
                    "personality": {
                        "traits": leader_term.traits,
                        "ideology": leader_term.ideology,
                        "risk_tolerance": leader_term.risk_tolerance,
                        "communication_style": "Direct and strategic.",
                    },
                    "decision_framework": {
                        "priorities": ["national_security", "economic_growth", "stability"],
                        "red_lines": ["territorial_integrity"],
                        "negotiation_style": "Pragmatic",
                    },
                    "worldview": {"key_beliefs": ["National interest first"]},
                }
        return None

    # ── main turn loop ─────────────────────────────────────────

    async def run_turn(self) -> dict[str, Any]:
        """Execute a single simulation turn with ALL subsystems integrated."""
        turn = self.world.turn
        year = self.world.year

        # ── 1. Leader transitions ──────────────────────────────
        leader_transitions = await self._process_leader_transitions(turn, year)

        # ── 2. Random / historical crises ──────────────────────
        crises = await self.crisis_gen.roll_crises()

        # ── 3. Advance active wars ─────────────────────────────
        war_events = await self._advance_wars(turn, year)

        # ── 4. Shadow powers tick ──────────────────────────────
        shadow_events = await self._tick_shadow_powers(turn, year)

        # ── 5. AI leader decisions (via LeaderAgent) ───────────
        turn_decisions = await self._collect_leader_decisions(turn, year)

        # ── 6. Process actions (start wars, apply effects) ─────
        action_events = await self._process_decision_actions(turn, year, turn_decisions)

        # ── 7. Time engine tick (economy, population, year) ────
        alive = await self.time_engine.tick()

        # ── 8. Update predictions ──────────────────────────────
        if self.predictor:
            self.predictor.generate_all_predictions()

        # ── 9. Log everything ──────────────────────────────────
        self.decisions_log.append({
            "turn": turn,
            "year": year,
            "decisions": {
                code: dec.model_dump() if hasattr(dec, "model_dump") else dec
                for code, dec in turn_decisions.items()
            },
            "crises": [c.model_dump() for c in crises],
            "active_wars": self.war_sim.list_active_wars(),
        })

        if self.on_turn:
            await self.on_turn(turn, year, self.event_bus.history(last_n=10), turn_decisions)

        return {
            "turn": turn,
            "year": year,
            "decisions": {
                code: dec.model_dump() if hasattr(dec, "model_dump") else dec
                for code, dec in turn_decisions.items()
            },
            "active_wars": self.war_sim.list_active_wars(),
            "events": [
                {"title": e.title, "severity": e.severity.value, "category": e.category.value}
                for e in self.event_bus.history(last_n=20)
            ],
            "continue": alive,
        }

    # ── sub-steps ──────────────────────────────────────────────

    async def _process_leader_transitions(self, turn: int, year: int) -> list[dict[str, Any]]:
        transitions: list[dict[str, Any]] = []
        if not self.leader_system:
            return transitions

        stability_map = {c.code: c.domestic.stability for c in self.world.all_countries()}
        transitions = self.leader_system.check_transitions(year, stability_map)

        for trans in transitions:
            code = trans["country"]
            # Fix: sync leader_id on CountryState
            new_leader = self.leader_system.get_leader(code)
            country = self.world.get(code)
            if country and new_leader:
                country.leader_id = new_leader.leader_id

            # Rebuild LeaderAgent for this country
            if country:
                self._rebuild_leader_agent(country)

            severity = (
                EventSeverity.CRITICAL if trans["reason"] in ("coup", "revolution")
                else EventSeverity.HIGH if trans["reason"] == "death"
                else EventSeverity.MEDIUM
            )
            await self.event_bus.publish(SimEvent(
                turn=turn, year=year,
                category=EventCategory.POLITICAL,
                severity=severity,
                title=f"{code}: Leadership Change ({trans['reason']})",
                description=f"{trans.get('old_leader', '?')} replaced by {trans['new_leader']}",
                source_country=code,
            ))
        return transitions

    def _rebuild_leader_agent(self, country: CountryState) -> None:
        """Rebuild LeaderAgent after a leader change (fresh memory, new profile)."""
        from agents.leader_agent import LeaderAgent

        profile = self._resolve_leader_profile(country)
        if not profile:
            self._leader_agents.pop(country.code, None)
            return

        agent = LeaderAgent(
            leader_profile=profile,
            country=country,
            llm=self.llm,
            use_advisors=self.use_advisors,
            use_vector_memory=False,
        )
        self._leader_agents[country.code] = agent

    async def _advance_wars(self, turn: int, year: int) -> list[SimEvent]:
        """Advance all active wars by one phase."""
        events_before = self.event_bus.total_events
        active_ids = self.war_sim.list_active_wars()
        for war_id in active_ids:
            report = await self.war_sim.advance_war(war_id)
            if report and report.outcome:
                # Apply final war effects
                attacker = self.world.get(report.attacker)
                defender = self.world.get(report.defender)
                if attacker and defender:
                    self._apply_war_outcome(report)
        return self.event_bus.history(last_n=self.event_bus.total_events - events_before)

    def _apply_war_outcome(self, report: Any) -> None:
        """Apply lasting effects when a war concludes."""
        from engine.war_simulator import WarOutcome

        attacker = self.world.get(report.attacker)
        defender = self.world.get(report.defender)
        if not attacker or not defender:
            return

        if report.outcome == WarOutcome.ATTACKER_VICTORY:
            defender.domestic.stability = max(0.05, defender.domestic.stability - 0.3)
            defender.economy.gdp_growth -= 5.0
            attacker.domestic.stability = min(1.0, attacker.domestic.stability + 0.05)
        elif report.outcome == WarOutcome.DEFENDER_VICTORY:
            attacker.domestic.stability = max(0.05, attacker.domestic.stability - 0.2)
            attacker.economy.gdp_growth -= 3.0
            defender.domestic.stability = min(1.0, defender.domestic.stability + 0.1)
        elif report.outcome == WarOutcome.NUCLEAR_EXCHANGE:
            for c in (attacker, defender):
                c.domestic.stability = max(0.01, c.domestic.stability - 0.5)
                c.economy.gdp_trillion *= 0.5
                c.domestic.population_million *= 0.7
        elif report.outcome in (WarOutcome.CEASEFIRE, WarOutcome.STALEMATE):
            attacker.relations[report.defender] = RelationType.HOSTILE
            defender.relations[report.attacker] = RelationType.HOSTILE

    async def _tick_shadow_powers(self, turn: int, year: int) -> list[dict[str, Any]]:
        """Run shadow power activities for this turn."""
        active_wars = [
            (r.attacker, r.defender)
            for r in self.war_sim.active_wars.values()
            if r.outcome is None
        ]
        stability_map = {c.code: c.domestic.stability for c in self.world.all_countries()}
        shadow_events = self.shadow_powers.tick(year, active_wars, stability_map)

        for se in shadow_events:
            if se.get("type") == "war_profiteering":
                await self.event_bus.publish(SimEvent(
                    turn=turn, year=year,
                    category=EventCategory.ECONOMIC,
                    severity=EventSeverity.MEDIUM,
                    title=f"War Profiteering: {se.get('entity', '?')}",
                    description=f"${se.get('revenue_boost_billion', 0):.1f}B revenue boost from conflict",
                ))
            elif se.get("type") == "pmc_deployment":
                country = self.world.get(se.get("country", ""))
                if country:
                    country.domestic.stability = min(1.0, country.domestic.stability + 0.02)
                await self.event_bus.publish(SimEvent(
                    turn=turn, year=year,
                    category=EventCategory.MILITARY,
                    severity=EventSeverity.MEDIUM,
                    title=f"PMC Deployment: {se.get('entity', '?')} → {se.get('country', '?')}",
                    description=f"{se.get('personnel', 0):,} personnel deployed",
                    source_country=se.get("country"),
                ))
        return shadow_events

    async def _collect_leader_decisions(self, turn: int, year: int) -> dict[str, Any]:
        """Collect AI decisions from LeaderAgents for top countries."""
        from agents.decision import LeaderDecision

        recent_events = self.event_bus.history(last_n=10)
        all_countries = self.world.all_countries()
        turn_decisions: dict[str, LeaderDecision | dict] = {}

        top_countries = self.world.ranked_by_power()[:20]

        for country in top_countries:
            if not country.leader_id:
                continue
            if (
                self.config.game_mode == GameMode.LEADER
                and country.code == self.config.player_country
            ):
                continue

            agent = self._leader_agents.get(country.code)
            if agent:
                # Update agent's country reference to current state
                agent.country = country
                try:
                    decision = await agent.make_decision(
                        turn=turn,
                        year=year,
                        recent_events=recent_events,
                        all_countries=all_countries,
                    )
                    turn_decisions[country.code] = decision
                except Exception as e:
                    turn_decisions[country.code] = self._fallback_decision(country, turn, year, e)
            else:
                # Fallback: direct LLM call for countries without agents
                profile = self._resolve_leader_profile(country)
                if not profile:
                    continue
                decision = await self._direct_llm_decision(
                    profile, country, turn, year, recent_events, all_countries
                )
                turn_decisions[country.code] = decision

        return turn_decisions

    def _fallback_decision(self, country: CountryState, turn: int, year: int, error: Exception) -> dict[str, Any]:
        return {
            "inner_thoughts": f"[AI Error: {error}]",
            "public_statement": "No comment at this time.",
            "actions": [{"type": "no_action", "target": "global", "detail": "Waiting", "intensity": 0.1}],
            "mood": "anxious",
            "leader_id": country.leader_id or "",
            "country_code": country.code,
            "turn": turn,
            "year": year,
        }

    async def _direct_llm_decision(
        self,
        profile: dict[str, Any],
        country: CountryState,
        turn: int,
        year: int,
        recent_events: list[SimEvent],
        all_countries: list[CountryState],
    ) -> dict[str, Any]:
        """Legacy direct LLM call for countries without a LeaderAgent."""
        world_summary = build_world_summary(all_countries)
        system_prompt = build_leader_system_prompt(profile, country)
        turn_prompt = build_turn_prompt(turn, year, recent_events, world_summary)
        try:
            return await self.llm.generate_structured(
                prompt=turn_prompt,
                schema=DECISION_SCHEMA,
                system=system_prompt,
            )
        except Exception as e:
            return self._fallback_decision(country, turn, year, e)

    async def _process_decision_actions(
        self, turn: int, year: int, turn_decisions: dict[str, Any]
    ) -> list[SimEvent]:
        """Process leader actions: publish events, start wars if military actions target specific countries."""
        from agents.decision import LeaderDecision, ActionType

        events_before = self.event_bus.total_events

        for code, decision in turn_decisions.items():
            country = self.world.get(code)
            if not country:
                continue

            actions: list[dict[str, Any]] = []
            if isinstance(decision, LeaderDecision):
                actions = [a.model_dump() for a in decision.actions]
            elif isinstance(decision, dict):
                actions = decision.get("actions", [])

            for action in actions:
                action_type = action.get("type", "no_action")
                target = action.get("target", "global")
                intensity = float(action.get("intensity", 0.5))
                detail = action.get("detail", "")

                await self.event_bus.publish(SimEvent(
                    turn=turn, year=year,
                    category=self._action_to_category(action_type),
                    severity=self._intensity_to_severity(intensity),
                    title=f"{country.name}: {action_type.replace('_', ' ').title()}",
                    description=detail,
                    source_country=code,
                    target_countries=[target] if target != "global" else [],
                ))

                # Auto-start war if high-intensity military action targets a country
                if (
                    action_type in ("military", "threaten")
                    and intensity >= 0.8
                    and target != "global"
                    and target not in ("global", code)
                ):
                    existing_war = any(
                        (r.attacker == code and r.defender == target) or
                        (r.attacker == target and r.defender == code)
                        for r in self.war_sim.active_wars.values()
                        if r.outcome is None
                    )
                    if not existing_war:
                        try:
                            await self.war_sim.start_war(code, target, casus_belli=detail or "military escalation")
                        except (ValueError, KeyError):
                            pass

        return self.event_bus.history(last_n=max(0, self.event_bus.total_events - events_before))

    # ── full run ───────────────────────────────────────────────

    async def run(self, turns: int | None = None) -> None:
        """Run the full simulation loop."""
        max_turns = turns or self.config.max_turns
        for _ in range(max_turns):
            result = await self.run_turn()
            if not result["continue"]:
                break

    # ── helpers ─────────────────────────────────────────────────

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

    # ── state serialization ────────────────────────────────────

    def get_state_snapshot(self) -> dict[str, Any]:
        """Full serializable snapshot of current simulation state."""
        return {
            "turn": self.world.turn,
            "year": self.world.year,
            "countries": {
                code: c.model_dump()
                for code, c in self.world.countries.items()
            },
            "active_wars": {
                wid: r.model_dump()
                for wid, r in self.war_sim.active_wars.items()
            },
            "decisions_log": self.decisions_log,
            "events": [e.model_dump() for e in self.event_bus.history(last_n=50)],
        }
