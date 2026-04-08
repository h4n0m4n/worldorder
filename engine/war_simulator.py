"""War Simulator — realistic military conflict modeling.

Uses Lanchester's Laws, real military data, logistics, terrain,
alliance chains, and nuclear deterrence to simulate wars.
Users can manually start wars and read detailed scenario outcomes.
"""

from __future__ import annotations

import math
import random
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from engine.world_state import WorldState, CountryState, RelationType, MilitaryStats
from engine.event_bus import EventBus, SimEvent, EventCategory, EventSeverity


class WarPhase(str, Enum):
    MOBILIZATION = "mobilization"
    INITIAL_STRIKE = "initial_strike"
    GROUND_OFFENSIVE = "ground_offensive"
    ATTRITION = "attrition"
    STALEMATE = "stalemate"
    ESCALATION = "escalation"
    CEASEFIRE = "ceasefire"
    SURRENDER = "surrender"
    NUCLEAR_THREAT = "nuclear_threat"


class WarOutcome(str, Enum):
    ATTACKER_VICTORY = "attacker_victory"
    DEFENDER_VICTORY = "defender_victory"
    STALEMATE = "stalemate"
    CEASEFIRE = "ceasefire"
    NUCLEAR_EXCHANGE = "nuclear_exchange"
    MUTUAL_DESTRUCTION = "mutual_destruction"


class BattlefieldReport(BaseModel):
    attacker: str
    defender: str
    attacker_allies: list[str] = Field(default_factory=list)
    defender_allies: list[str] = Field(default_factory=list)
    phase: WarPhase = WarPhase.MOBILIZATION
    turn_started: int = 0
    turns_elapsed: int = 0

    # Force calculations
    attacker_power: float = 0.0
    defender_power: float = 0.0
    power_ratio: float = 1.0

    # Casualties
    attacker_casualties: int = 0
    defender_casualties: int = 0
    civilian_casualties: int = 0

    # Economic impact
    attacker_gdp_loss_pct: float = 0.0
    defender_gdp_loss_pct: float = 0.0
    global_gdp_impact_pct: float = 0.0

    # Nuclear
    nuclear_risk: float = 0.0
    nuclear_used: bool = False

    # Outcome
    outcome: WarOutcome | None = None
    outcome_probability: dict[str, float] = Field(default_factory=dict)

    # Narrative
    narrative: list[str] = Field(default_factory=list)
    key_events: list[str] = Field(default_factory=list)

    # Shadow powers
    arms_suppliers_attacker: list[str] = Field(default_factory=list)
    arms_suppliers_defender: list[str] = Field(default_factory=list)
    war_profiteers: list[dict[str, Any]] = Field(default_factory=list)


class WarSimulator:
    """Full-featured war simulation engine."""

    def __init__(
        self,
        world: WorldState,
        event_bus: EventBus,
        rng_seed: int | None = None,
    ) -> None:
        self.world = world
        self.event_bus = event_bus
        self.rng = random.Random(rng_seed)
        self.active_wars: dict[str, BattlefieldReport] = {}  # war_id -> report

    def calculate_combat_power(self, country: CountryState, allies: list[CountryState] | None = None) -> float:
        """Calculate total combat power using modified Lanchester model.

        Factors: military index, GDP (war economy), tech level, nuclear,
        population (manpower), stability (morale), terrain advantage.
        """
        m = country.military
        e = country.economy
        d = country.domestic

        base_power = m.power_index * 100

        # Lanchester's Square Law: power proportional to N^2 * quality
        personnel_factor = math.sqrt(m.active_personnel / 100_000) * 5
        quality_factor = (m.air_strength + m.navy_strength + m.cyber_capability) / 3

        # Economic war capacity
        war_economy = math.log10(max(0.01, e.gdp_trillion) + 1) * 15

        # Technology multiplier
        tech_mult = 1.0 + d.tech_level * 0.5

        # Morale/stability
        morale = d.stability * 0.8 + 0.2

        # Nuclear deterrence bonus
        nuke_bonus = 30 if m.nuclear else 0

        total = (base_power + personnel_factor * quality_factor + war_economy) * tech_mult * morale + nuke_bonus

        # Add allied power (at 60% effectiveness due to coordination costs)
        if allies:
            for ally in allies:
                ally_power = self.calculate_combat_power(ally) * 0.6
                total += ally_power

        return round(total, 1)

    def find_allies(self, country_code: str, against: str) -> list[str]:
        """Find which countries would join as allies in a war."""
        country = self.world.get(country_code)
        if not country:
            return []

        allies = []
        for c in self.world.all_countries():
            if c.code == country_code or c.code == against:
                continue
            # Formal alliance
            shared_alliances = set(country.alliances) & set(c.alliances)
            if shared_alliances and len(shared_alliances) > 0:
                # Check if they're not also allied with the enemy
                enemy = self.world.get(against)
                if enemy:
                    enemy_shared = set(enemy.alliances) & set(c.alliances)
                    if not enemy_shared:
                        allies.append(c.code)
            # Direct hostile relationship with the target
            rel = c.relation_with(against)
            if rel in (RelationType.HOSTILE, RelationType.WAR):
                if c.code not in allies:
                    allies.append(c.code)

        return allies

    async def start_war(
        self,
        attacker_code: str,
        defender_code: str,
        casus_belli: str = "territorial dispute",
    ) -> BattlefieldReport:
        """Manually start a war between two countries."""
        attacker = self.world.get(attacker_code)
        defender = self.world.get(defender_code)
        if not attacker or not defender:
            raise ValueError(f"Country not found: {attacker_code} or {defender_code}")

        war_id = f"{attacker_code}_vs_{defender_code}_{self.world.turn}"

        # Find allies
        att_allies = self.find_allies(attacker_code, defender_code)
        def_allies = self.find_allies(defender_code, attacker_code)

        att_ally_states = [self.world.get(a) for a in att_allies if self.world.get(a)]
        def_ally_states = [self.world.get(d) for d in def_allies if self.world.get(d)]

        att_power = self.calculate_combat_power(attacker, att_ally_states)
        def_power = self.calculate_combat_power(defender, def_ally_states)
        ratio = att_power / max(def_power, 0.1)

        # Nuclear risk assessment
        nuclear_risk = 0.0
        if attacker.military.nuclear and defender.military.nuclear:
            nuclear_risk = 0.15  # MAD baseline
            if ratio < 0.5 or ratio > 2.0:
                nuclear_risk += 0.10  # desperate side might escalate
        elif attacker.military.nuclear or defender.military.nuclear:
            nuclear_risk = 0.05
            losing_side_nuclear = (
                (attacker.military.nuclear and ratio < 0.7) or
                (defender.military.nuclear and ratio > 1.5)
            )
            if losing_side_nuclear:
                nuclear_risk += 0.15

        # Calculate outcome probabilities
        outcome_probs = self._calculate_outcome_probabilities(ratio, nuclear_risk, attacker, defender)

        # Estimate casualties (Lanchester attrition)
        total_personnel = attacker.military.active_personnel + defender.military.active_personnel
        base_casualty_rate = 0.05  # 5% of total forces per phase
        att_casualties = int(defender.military.power_index * total_personnel * base_casualty_rate)
        def_casualties = int(attacker.military.power_index * total_personnel * base_casualty_rate * 1.2)
        civilian_casualties = int((att_casualties + def_casualties) * 0.5)

        # Economic impact
        att_gdp_loss = min(30, 5 + (1 / max(ratio, 0.1)) * 10)
        def_gdp_loss = min(50, 10 + ratio * 15)
        global_impact = (attacker.economy.gdp_trillion + defender.economy.gdp_trillion) / 100 * 2

        # Build narrative
        narrative = self._build_war_narrative(
            attacker, defender, att_allies, def_allies, ratio, nuclear_risk, casus_belli
        )

        report = BattlefieldReport(
            attacker=attacker_code,
            defender=defender_code,
            attacker_allies=att_allies,
            defender_allies=def_allies,
            phase=WarPhase.MOBILIZATION,
            turn_started=self.world.turn,
            attacker_power=att_power,
            defender_power=def_power,
            power_ratio=round(ratio, 2),
            attacker_casualties=att_casualties,
            defender_casualties=def_casualties,
            civilian_casualties=civilian_casualties,
            attacker_gdp_loss_pct=round(att_gdp_loss, 1),
            defender_gdp_loss_pct=round(def_gdp_loss, 1),
            global_gdp_impact_pct=round(global_impact, 2),
            nuclear_risk=round(nuclear_risk, 3),
            outcome_probability=outcome_probs,
            narrative=narrative,
        )

        self.active_wars[war_id] = report

        # Apply war state
        self.world.apply_war_effects(attacker_code, defender_code)

        # Publish events
        await self.event_bus.publish(SimEvent(
            turn=self.world.turn, year=self.world.year,
            category=EventCategory.MILITARY,
            severity=EventSeverity.CRITICAL,
            title=f"WAR: {attacker.name} attacks {defender.name}",
            description=f"Casus belli: {casus_belli}. Power ratio: {ratio:.1f}:1. Nuclear risk: {nuclear_risk:.0%}",
            source_country=attacker_code,
            target_countries=[defender_code],
        ))

        if att_allies:
            await self.event_bus.publish(SimEvent(
                turn=self.world.turn, year=self.world.year,
                category=EventCategory.MILITARY, severity=EventSeverity.HIGH,
                title=f"Alliance activation: {', '.join(att_allies)} join {attacker.name}",
                description=f"{len(att_allies)} nations mobilize in support of the attacker.",
                source_country=attacker_code,
            ))

        if def_allies:
            await self.event_bus.publish(SimEvent(
                turn=self.world.turn, year=self.world.year,
                category=EventCategory.MILITARY, severity=EventSeverity.HIGH,
                title=f"Alliance activation: {', '.join(def_allies)} defend {defender.name}",
                description=f"{len(def_allies)} nations mobilize in defense.",
                source_country=defender_code,
            ))

        return report

    def _calculate_outcome_probabilities(
        self, ratio: float, nuclear_risk: float, attacker: CountryState, defender: CountryState
    ) -> dict[str, float]:
        """Calculate probability of each war outcome."""
        # Base probabilities from power ratio
        if ratio > 3.0:
            att_win, def_win, stalemate = 0.70, 0.05, 0.15
        elif ratio > 2.0:
            att_win, def_win, stalemate = 0.55, 0.10, 0.25
        elif ratio > 1.5:
            att_win, def_win, stalemate = 0.40, 0.15, 0.30
        elif ratio > 1.0:
            att_win, def_win, stalemate = 0.30, 0.20, 0.35
        elif ratio > 0.7:
            att_win, def_win, stalemate = 0.20, 0.30, 0.35
        elif ratio > 0.5:
            att_win, def_win, stalemate = 0.10, 0.45, 0.30
        else:
            att_win, def_win, stalemate = 0.05, 0.60, 0.20

        ceasefire = 1.0 - att_win - def_win - stalemate - nuclear_risk
        ceasefire = max(0.05, ceasefire)

        # Normalize
        total = att_win + def_win + stalemate + ceasefire + nuclear_risk
        return {
            "attacker_victory": round(att_win / total, 3),
            "defender_victory": round(def_win / total, 3),
            "stalemate": round(stalemate / total, 3),
            "ceasefire": round(ceasefire / total, 3),
            "nuclear_exchange": round(nuclear_risk / total, 3),
        }

    def _build_war_narrative(
        self,
        attacker: CountryState,
        defender: CountryState,
        att_allies: list[str],
        def_allies: list[str],
        ratio: float,
        nuclear_risk: float,
        casus_belli: str,
    ) -> list[str]:
        """Generate a detailed war narrative."""
        lines = []
        lines.append(f"═══ WAR ANALYSIS: {attacker.name} vs {defender.name} ═══")
        lines.append(f"Casus Belli: {casus_belli}")
        lines.append("")

        # Force comparison
        lines.append("FORCE COMPARISON:")
        lines.append(f"  {attacker.name}: Power {attacker.military.power_index:.0%} | "
                     f"{attacker.military.active_personnel:,} troops | "
                     f"{'NUCLEAR' if attacker.military.nuclear else 'Conventional'}")
        lines.append(f"  {defender.name}: Power {defender.military.power_index:.0%} | "
                     f"{defender.military.active_personnel:,} troops | "
                     f"{'NUCLEAR' if defender.military.nuclear else 'Conventional'}")
        lines.append(f"  Power Ratio: {ratio:.2f}:1 {'(Attacker advantage)' if ratio > 1 else '(Defender advantage)'}")
        lines.append("")

        # Alliances
        if att_allies or def_allies:
            lines.append("ALLIANCE CHAINS:")
            if att_allies:
                lines.append(f"  Attacker coalition: {attacker.code} + {', '.join(att_allies)}")
            if def_allies:
                lines.append(f"  Defender coalition: {defender.code} + {', '.join(def_allies)}")
            lines.append("")

        # Economic warfare
        lines.append("ECONOMIC IMPACT:")
        lines.append(f"  {attacker.name} GDP: ${attacker.economy.gdp_trillion:.1f}T (war cost est. 5-15%)")
        lines.append(f"  {defender.name} GDP: ${defender.economy.gdp_trillion:.1f}T (war cost est. 10-30%)")
        lines.append(f"  Global supply chain disruption: SIGNIFICANT")
        lines.append("")

        # Nuclear assessment
        if nuclear_risk > 0:
            lines.append(f"NUCLEAR RISK: {nuclear_risk:.0%}")
            if attacker.military.nuclear and defender.military.nuclear:
                lines.append("  ⚠ MUTUAL ASSURED DESTRUCTION scenario possible")
                lines.append("  Both sides possess nuclear weapons — escalation ladder is extremely dangerous")
            elif attacker.military.nuclear:
                lines.append(f"  {attacker.name} has nuclear capability — may use as last resort")
            else:
                lines.append(f"  {defender.name} has nuclear capability — may use if facing defeat")
            lines.append("")

        # Scenario phases
        lines.append("PROJECTED PHASES:")
        if ratio > 2.0:
            lines.append("  Phase 1: Rapid air/missile strikes neutralize defender air defense")
            lines.append("  Phase 2: Ground offensive with overwhelming force")
            lines.append("  Phase 3: Occupation or regime change within weeks-months")
        elif ratio > 1.0:
            lines.append("  Phase 1: Initial strikes with contested air superiority")
            lines.append("  Phase 2: Grinding ground campaign, urban warfare likely")
            lines.append("  Phase 3: Prolonged conflict, international pressure for ceasefire")
        else:
            lines.append("  Phase 1: Defender repels initial assault")
            lines.append("  Phase 2: Attacker bogged down, attrition warfare")
            lines.append("  Phase 3: Possible attacker withdrawal or stalemate")

        return lines

    async def advance_war(self, war_id: str) -> BattlefieldReport | None:
        """Advance a war by one phase."""
        report = self.active_wars.get(war_id)
        if not report or report.outcome:
            return report

        report.turns_elapsed += 1

        # Phase progression
        phase_order = [
            WarPhase.MOBILIZATION, WarPhase.INITIAL_STRIKE,
            WarPhase.GROUND_OFFENSIVE, WarPhase.ATTRITION,
        ]
        current_idx = phase_order.index(report.phase) if report.phase in phase_order else 0
        if current_idx < len(phase_order) - 1:
            report.phase = phase_order[current_idx + 1]

        # Attrition each turn
        att_loss = int(report.defender_power * 500 * self.rng.uniform(0.5, 1.5))
        def_loss = int(report.attacker_power * 600 * self.rng.uniform(0.5, 1.5))
        report.attacker_casualties += att_loss
        report.defender_casualties += def_loss
        report.civilian_casualties += int((att_loss + def_loss) * 0.3)

        # Check for resolution
        if report.turns_elapsed >= 3:
            roll = self.rng.random()
            cumulative = 0.0
            for outcome_str, prob in report.outcome_probability.items():
                cumulative += prob
                if roll <= cumulative:
                    report.outcome = WarOutcome(outcome_str)
                    break

            if report.outcome:
                report.key_events.append(f"Year {self.world.year}: War ends — {report.outcome.value}")
                await self.event_bus.publish(SimEvent(
                    turn=self.world.turn, year=self.world.year,
                    category=EventCategory.MILITARY,
                    severity=EventSeverity.CRITICAL,
                    title=f"WAR ENDS: {report.attacker} vs {report.defender} — {report.outcome.value}",
                    description=f"After {report.turns_elapsed} turns. Casualties: {report.attacker_casualties + report.defender_casualties:,}",
                    source_country=report.attacker,
                    target_countries=[report.defender],
                ))

        return report

    def get_war_report(self, war_id: str) -> BattlefieldReport | None:
        return self.active_wars.get(war_id)

    def list_active_wars(self) -> list[str]:
        return [wid for wid, r in self.active_wars.items() if r.outcome is None]

    def generate_scenario_analysis(self, attacker_code: str, defender_code: str) -> list[str]:
        """Generate a what-if analysis without actually starting the war."""
        attacker = self.world.get(attacker_code)
        defender = self.world.get(defender_code)
        if not attacker or not defender:
            return [f"Country not found: {attacker_code} or {defender_code}"]

        att_allies = self.find_allies(attacker_code, defender_code)
        def_allies = self.find_allies(defender_code, attacker_code)

        att_ally_states = [self.world.get(a) for a in att_allies if self.world.get(a)]
        def_ally_states = [self.world.get(d) for d in def_allies if self.world.get(d)]

        att_power = self.calculate_combat_power(attacker, att_ally_states)
        def_power = self.calculate_combat_power(defender, def_ally_states)
        ratio = att_power / max(def_power, 0.1)

        nuclear_risk = 0.0
        if attacker.military.nuclear and defender.military.nuclear:
            nuclear_risk = 0.15
        elif attacker.military.nuclear or defender.military.nuclear:
            nuclear_risk = 0.05

        probs = self._calculate_outcome_probabilities(ratio, nuclear_risk, attacker, defender)
        narrative = self._build_war_narrative(attacker, defender, att_allies, def_allies, ratio, nuclear_risk, "hypothetical")

        narrative.append("")
        narrative.append("OUTCOME PROBABILITIES:")
        for outcome, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(prob * 40) + "░" * (40 - int(prob * 40))
            narrative.append(f"  {outcome:25s} [{bar}] {prob:.1%}")

        return narrative
