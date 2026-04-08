"""Crisis Generator — injects random or historical crises into the simulation."""

from __future__ import annotations

import random
from typing import Any

from pydantic import BaseModel, Field

from engine.event_bus import EventBus, SimEvent, EventCategory, EventSeverity
from engine.world_state import WorldState


class CrisisTemplate(BaseModel):
    id: str
    title: str
    description: str
    category: EventCategory
    severity: EventSeverity = EventSeverity.HIGH
    probability: float = 0.05  # per turn
    effects: dict[str, Any] = Field(default_factory=dict)
    target_regions: list[str] = Field(default_factory=list)
    min_year: int = -3000
    max_year: int = 2100


BUILTIN_CRISES: list[CrisisTemplate] = [
    CrisisTemplate(
        id="oil_shock",
        title="Global Oil Supply Shock",
        description="Major oil-producing region faces disruption, prices spike worldwide.",
        category=EventCategory.ECONOMIC,
        severity=EventSeverity.CRITICAL,
        probability=0.04,
        effects={"oil_price_multiplier": 2.5, "inflation_add": 3.0, "stability_sub": 0.1},
    ),
    CrisisTemplate(
        id="pandemic",
        title="Global Pandemic Outbreak",
        description="A novel pathogen spreads across continents, overwhelming health systems.",
        category=EventCategory.SOCIAL,
        severity=EventSeverity.CRITICAL,
        probability=0.02,
        effects={"gdp_growth_sub": 4.0, "stability_sub": 0.15, "unemployment_add": 5.0},
    ),
    CrisisTemplate(
        id="financial_crash",
        title="Global Financial Crisis",
        description="Cascading bank failures trigger worldwide recession.",
        category=EventCategory.ECONOMIC,
        severity=EventSeverity.CRITICAL,
        probability=0.03,
        effects={"gdp_growth_sub": 3.0, "debt_add": 15.0, "unemployment_add": 4.0},
    ),
    CrisisTemplate(
        id="cyber_attack",
        title="State-Sponsored Cyber Warfare",
        description="Critical infrastructure targeted in coordinated cyber assault.",
        category=EventCategory.TECHNOLOGICAL,
        severity=EventSeverity.HIGH,
        probability=0.05,
        effects={"stability_sub": 0.08, "tech_damage": 0.1},
    ),
    CrisisTemplate(
        id="climate_disaster",
        title="Extreme Climate Event",
        description="Unprecedented weather devastates agriculture and coastal regions.",
        category=EventCategory.ENVIRONMENTAL,
        severity=EventSeverity.HIGH,
        probability=0.06,
        effects={"food_sub": 0.2, "gdp_growth_sub": 1.5, "stability_sub": 0.05},
    ),
    CrisisTemplate(
        id="revolution",
        title="Popular Revolution",
        description="Mass protests topple the government, power vacuum emerges.",
        category=EventCategory.POLITICAL,
        severity=EventSeverity.CRITICAL,
        probability=0.03,
        effects={"stability_sub": 0.4, "democracy_shift": 0.2},
    ),
    CrisisTemplate(
        id="nuclear_threat",
        title="Nuclear Escalation Threat",
        description="A nuclear-armed state issues explicit first-strike warnings.",
        category=EventCategory.MILITARY,
        severity=EventSeverity.CRITICAL,
        probability=0.01,
        effects={"stability_sub": 0.2, "market_panic": True},
    ),
    CrisisTemplate(
        id="tech_breakthrough",
        title="Disruptive Technology Breakthrough",
        description="A major technological leap reshapes global power dynamics.",
        category=EventCategory.TECHNOLOGICAL,
        severity=EventSeverity.HIGH,
        probability=0.04,
        effects={"tech_boost": 0.15, "gdp_growth_add": 1.0},
    ),
    CrisisTemplate(
        id="refugee_crisis",
        title="Mass Refugee Crisis",
        description="Millions displaced by conflict or climate, straining neighboring nations.",
        category=EventCategory.SOCIAL,
        severity=EventSeverity.HIGH,
        probability=0.05,
        effects={"stability_sub": 0.1, "population_shift": True},
    ),
    CrisisTemplate(
        id="trade_war",
        title="Global Trade War",
        description="Major economies impose sweeping tariffs, fragmenting global trade.",
        category=EventCategory.ECONOMIC,
        severity=EventSeverity.HIGH,
        probability=0.05,
        effects={"gdp_growth_sub": 1.5, "trade_balance_shift": -0.3},
    ),
]


class CrisisGenerator:
    """Generates crises each turn based on probability and world state."""

    def __init__(
        self,
        world: WorldState,
        event_bus: EventBus,
        templates: list[CrisisTemplate] | None = None,
        rng_seed: int | None = None,
    ) -> None:
        self.world = world
        self.event_bus = event_bus
        self.templates = templates or BUILTIN_CRISES
        self.rng = random.Random(rng_seed)
        self._cooldowns: dict[str, int] = {}

    async def roll_crises(self) -> list[SimEvent]:
        """Roll for each crisis template; returns any that triggered."""
        triggered: list[SimEvent] = []
        for tpl in self.templates:
            if not (tpl.min_year <= self.world.year <= tpl.max_year):
                continue
            cooldown = self._cooldowns.get(tpl.id, 0)
            if cooldown > 0:
                self._cooldowns[tpl.id] = cooldown - 1
                continue
            if self.rng.random() < tpl.probability:
                event = SimEvent(
                    turn=self.world.turn,
                    year=self.world.year,
                    category=tpl.category,
                    severity=tpl.severity,
                    title=tpl.title,
                    description=tpl.description,
                    effects=tpl.effects,
                )
                await self.event_bus.publish(event)
                triggered.append(event)
                self._cooldowns[tpl.id] = 5  # min 5 turns between same crisis
                self._apply_effects(tpl)
        return triggered

    def _apply_effects(self, tpl: CrisisTemplate) -> None:
        """Apply crisis effects to world state."""
        effects = tpl.effects
        for c in self.world.all_countries():
            if "gdp_growth_sub" in effects:
                c.economy.gdp_growth -= effects["gdp_growth_sub"]
            if "gdp_growth_add" in effects:
                c.economy.gdp_growth += effects["gdp_growth_add"]
            if "inflation_add" in effects:
                c.economy.inflation += effects["inflation_add"]
            if "stability_sub" in effects:
                c.domestic.stability = max(0, c.domestic.stability - effects["stability_sub"])
            if "unemployment_add" in effects:
                c.economy.unemployment += effects["unemployment_add"]
            if "debt_add" in effects:
                c.economy.debt_to_gdp += effects["debt_add"]
            if "food_sub" in effects:
                c.resources.food_self_sufficiency = max(
                    0, c.resources.food_self_sufficiency - effects["food_sub"]
                )
            if "tech_boost" in effects:
                c.domestic.tech_level = min(1, c.domestic.tech_level + effects["tech_boost"])

    async def inject_custom(
        self,
        title: str,
        description: str,
        category: EventCategory = EventCategory.CRISIS,
        severity: EventSeverity = EventSeverity.CRITICAL,
        target_countries: list[str] | None = None,
    ) -> SimEvent:
        """Manually inject a 'What If?' crisis."""
        event = SimEvent(
            turn=self.world.turn,
            year=self.world.year,
            category=category,
            severity=severity,
            title=title,
            description=description,
            target_countries=target_countries or [],
        )
        await self.event_bus.publish(event)
        return event
