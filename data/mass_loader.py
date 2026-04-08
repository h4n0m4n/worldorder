"""Mass loader — loads all 195+ countries from world_database.py.

Combines the comprehensive database with YAML overrides for major countries.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.config import PROFILES_DIR
from engine.world_state import (
    CountryState,
    MilitaryStats,
    EconomyStats,
    ResourceStats,
    DomesticStats,
)
from data.world_database import COUNTRIES_RAW, TOTAL_COUNTRIES
from data.leader_generator import CURRENT_LEADERS_2025, DynamicLeaderSystem


def _estimate_resources(pop: float, gdp: float, region: str) -> ResourceStats:
    """Estimate resource stats from basic data."""
    oil_regions = {"Middle East", "North Africa", "Central Asia", "Eurasia"}
    gas_regions = {"Middle East", "Central Asia", "Eurasia", "North Africa"}

    return ResourceStats(
        oil_production=max(0, gdp * 0.5) if region in oil_regions else max(0, gdp * 0.05),
        gas_production=max(0, gdp * 0.3) if region in gas_regions else max(0, gdp * 0.02),
        rare_earth=0.01,
        food_self_sufficiency=min(0.95, max(0.3, 0.5 + (pop / 500) * 0.1)),
        water_stress=max(0.1, min(0.9, 0.3 + (0.5 if region in {"Middle East", "North Africa"} else 0))),
    )


def _estimate_economy(gdp: float, stability: float, tech: float) -> EconomyStats:
    """Build economy stats from basic data."""
    return EconomyStats(
        gdp_trillion=gdp,
        gdp_growth=max(-5, min(8, 2.0 + (1 - tech) * 3 - (1 - stability) * 2)),
        inflation=max(1, min(50, 3 + (1 - stability) * 15)),
        debt_to_gdp=max(10, min(250, 60 + (1 - stability) * 40)),
        unemployment=max(2, min(35, 5 + (1 - stability) * 15)),
        trade_balance=gdp * 10 * (tech - 0.5),
        currency_strength=max(0.05, min(0.95, stability * 0.5 + tech * 0.3 + gdp / 30 * 0.2)),
        sanctions_pressure=0.0,
    )


def load_all_countries_mass() -> list[CountryState]:
    """Load all countries from the comprehensive database."""
    countries: list[CountryState] = []

    for row in COUNTRIES_RAW:
        code, name, region, pop, gdp, mil, nuke, stab, demo, tech, gov = row

        country = CountryState(
            code=code,
            name=name,
            military=MilitaryStats(
                power_index=mil,
                nuclear=nuke,
                active_personnel=int(pop * 1000 * max(0.5, mil)),
                defense_budget_pct_gdp=max(0.5, mil * 5),
                navy_strength=mil * 0.5,
                air_strength=mil * 0.6,
                cyber_capability=tech * 0.7,
            ),
            economy=_estimate_economy(gdp, stab, tech),
            resources=_estimate_resources(pop, gdp, region),
            domestic=DomesticStats(
                stability=stab,
                democracy_index=demo,
                corruption=max(0.1, 1 - demo * 0.7 - stab * 0.2),
                press_freedom=demo * 0.85,
                population_million=pop,
                median_age=25 + demo * 10 + tech * 8,
                urbanization=max(0.2, min(0.95, 0.4 + tech * 0.4)),
                education_index=max(0.1, tech * 0.8 + demo * 0.15),
                tech_level=tech,
            ),
        )
        countries.append(country)

    return countries


def initialize_leaders(
    countries: list[CountryState],
    year: int = 2025,
    rng_seed: int | None = None,
) -> DynamicLeaderSystem:
    """Initialize the dynamic leader system for all countries."""
    system = DynamicLeaderSystem(rng_seed=rng_seed)

    for country in countries:
        code = country.code
        if code in CURRENT_LEADERS_2025:
            data = CURRENT_LEADERS_2025[code]
            leader = system.initialize_leader(
                country_code=code,
                name=data["name"],
                year=data.get("start_year", year),
                title=data.get("title", "Head of State"),
                ideology=data.get("ideology", ""),
                traits=data.get("traits", []),
                risk_tolerance=data.get("risk_tolerance", 0.5),
            )
            country.leader_id = leader.leader_id
        else:
            leader = system.initialize_leader(
                country_code=code,
                name=f"Leader of {country.name}",
                year=year,
                title="Head of State",
                traits=["pragmatic", "moderate"],
                risk_tolerance=0.5,
            )
            country.leader_id = leader.leader_id

    return system
