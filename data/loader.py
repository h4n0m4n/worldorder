"""Load country and leader profiles from YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from engine.config import PROFILES_DIR
from engine.world_state import (
    CountryState,
    MilitaryStats,
    EconomyStats,
    ResourceStats,
    DomesticStats,
)


def _read_yaml(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_country(path: Path) -> CountryState:
    raw = _read_yaml(path)
    return CountryState(
        code=raw["code"],
        name=raw["name"],
        military=MilitaryStats(**raw.get("military", {})),
        economy=EconomyStats(**raw.get("economy", {})),
        resources=ResourceStats(**raw.get("resources", {})),
        domestic=DomesticStats(**raw.get("domestic", {})),
        alliances=raw.get("alliances", []),
    )


def load_all_countries(directory: Path | None = None) -> list[CountryState]:
    directory = directory or PROFILES_DIR / "countries"
    countries = []
    for p in sorted(directory.glob("*.yaml")):
        countries.append(load_country(p))
    return countries


def load_leader_profile(path: Path) -> dict[str, Any]:
    return _read_yaml(path)


def load_all_leader_profiles(directory: Path | None = None) -> dict[str, dict[str, Any]]:
    directory = directory or PROFILES_DIR / "leaders"
    leaders: dict[str, dict[str, Any]] = {}
    for p in sorted(directory.glob("*.yaml")):
        profile = load_leader_profile(p)
        leaders[profile["id"]] = profile
    return leaders
