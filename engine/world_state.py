"""World State Manager — holds the full state of every nation each turn."""

from __future__ import annotations

import math
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RelationType(str, Enum):
    ALLIED = "allied"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    TENSE = "tense"
    HOSTILE = "hostile"
    WAR = "war"


class MilitaryStats(BaseModel):
    power_index: float = 0.5          # 0‑1 composite score
    nuclear: bool = False
    active_personnel: int = 100_000
    defense_budget_pct_gdp: float = 2.0
    navy_strength: float = 0.3
    air_strength: float = 0.3
    cyber_capability: float = 0.2


class EconomyStats(BaseModel):
    gdp_trillion: float = 0.5
    gdp_growth: float = 2.0           # annual %
    inflation: float = 3.0
    debt_to_gdp: float = 60.0
    unemployment: float = 6.0
    trade_balance: float = 0.0        # billion $
    currency_strength: float = 0.5    # 0‑1
    sanctions_pressure: float = 0.0   # 0‑1


class ResourceStats(BaseModel):
    oil_production: float = 0.0       # million bbl/day
    gas_production: float = 0.0
    rare_earth: float = 0.0
    food_self_sufficiency: float = 0.7  # 0‑1
    water_stress: float = 0.3         # 0‑1


class DomesticStats(BaseModel):
    stability: float = 0.7            # 0‑1
    democracy_index: float = 0.5      # 0‑1
    corruption: float = 0.4           # 0‑1
    press_freedom: float = 0.5
    population_million: float = 50.0
    median_age: float = 30.0
    urbanization: float = 0.6
    education_index: float = 0.6
    tech_level: float = 0.5           # 0‑1


class CountryState(BaseModel):
    code: str                         # ISO 3166 alpha‑2
    name: str
    leader_id: str | None = None
    military: MilitaryStats = Field(default_factory=MilitaryStats)
    economy: EconomyStats = Field(default_factory=EconomyStats)
    resources: ResourceStats = Field(default_factory=ResourceStats)
    domestic: DomesticStats = Field(default_factory=DomesticStats)
    alliances: list[str] = Field(default_factory=list)
    relations: dict[str, RelationType] = Field(default_factory=dict)
    flags: dict[str, Any] = Field(default_factory=dict)

    @property
    def composite_power(self) -> float:
        """Rough composite national power score 0‑100."""
        mil = self.military.power_index * 30
        eco = min(self.economy.gdp_trillion / 25, 1.0) * 30
        tech = self.domestic.tech_level * 20
        stab = self.domestic.stability * 10
        pop = min(self.domestic.population_million / 1500, 1.0) * 10
        return round(mil + eco + tech + stab + pop, 1)

    def relation_with(self, other_code: str) -> RelationType:
        return self.relations.get(other_code, RelationType.NEUTRAL)


class WorldState:
    """Snapshot of the entire world at a given turn."""

    def __init__(self) -> None:
        self.turn: int = 0
        self.year: int = 2025
        self.countries: dict[str, CountryState] = {}
        self._snapshots: list[dict[str, Any]] = []

    def add_country(self, country: CountryState) -> None:
        self.countries[country.code] = country

    def get(self, code: str) -> CountryState | None:
        return self.countries.get(code)

    def all_countries(self) -> list[CountryState]:
        return list(self.countries.values())

    def ranked_by_power(self) -> list[CountryState]:
        return sorted(self.all_countries(), key=lambda c: c.composite_power, reverse=True)

    def advance_turn(self, years: int = 1) -> None:
        self._snapshots.append(self._serialize())
        self.turn += 1
        self.year += years

    def apply_economic_tick(self) -> None:
        """Natural economic drift each turn."""
        for c in self.countries.values():
            e = c.economy
            e.gdp_trillion *= 1 + e.gdp_growth / 100
            e.debt_to_gdp += max(0, (e.inflation - 2) * 0.3)
            c.domestic.stability = max(0, min(1, c.domestic.stability - (e.inflation - 4) * 0.01))

    def apply_population_tick(self) -> None:
        for c in self.countries.values():
            growth = 0.01 * (1 - c.domestic.median_age / 80)
            c.domestic.population_million *= 1 + growth

    def apply_war_effects(self, attacker: str, defender: str) -> None:
        a, d = self.get(attacker), self.get(defender)
        if not a or not d:
            return
        a.economy.gdp_growth -= 2.0
        d.economy.gdp_growth -= 4.0
        a.domestic.stability -= 0.1
        d.domestic.stability -= 0.2
        a.military.active_personnel = int(a.military.active_personnel * 0.95)
        d.military.active_personnel = int(d.military.active_personnel * 0.90)
        a.relations[defender] = RelationType.WAR
        d.relations[attacker] = RelationType.WAR

    def _serialize(self) -> dict[str, Any]:
        return {
            "turn": self.turn,
            "year": self.year,
            "countries": {k: v.model_dump() for k, v in self.countries.items()},
        }

    def rewind(self, to_turn: int) -> bool:
        if to_turn < 0 or to_turn >= len(self._snapshots):
            return False
        snap = self._snapshots[to_turn]
        self.turn = snap["turn"]
        self.year = snap["year"]
        self.countries = {
            k: CountryState(**v) for k, v in snap["countries"].items()
        }
        self._snapshots = self._snapshots[: to_turn]
        return True
