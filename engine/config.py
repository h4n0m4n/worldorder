"""Global simulation configuration."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROFILES_DIR = DATA_DIR / "profiles"


class Era(str, Enum):
    ANCIENT = "ancient"       # 3000 BC – 500 AD
    MEDIEVAL = "medieval"     # 500 – 1500
    EARLY_MODERN = "early_modern"  # 1500 – 1800
    MODERN = "modern"         # 1800 – 2000
    CONTEMPORARY = "contemporary"  # 2000 – present
    FUTURE = "future"         # present – 2100


class TimeScale(str, Enum):
    DECADE = "decade"
    YEAR = "year"
    MONTH = "month"


class GameMode(str, Enum):
    GOD = "god"       # observe & intervene
    LEADER = "leader"  # play as a country leader


class SimulationConfig(BaseModel):
    era: Era = Era.CONTEMPORARY
    start_year: int = 2025
    end_year: int = 2100
    time_scale: TimeScale = TimeScale.YEAR
    game_mode: GameMode = GameMode.GOD
    player_country: str | None = None
    max_turns: int = 100
    llm_provider: str = "ollama"
    llm_model: str = "llama3.1"
    seed: int | None = None
    extra: dict[str, Any] = Field(default_factory=dict)

    def turns_label(self) -> str:
        return {
            TimeScale.DECADE: "decades",
            TimeScale.YEAR: "years",
            TimeScale.MONTH: "months",
        }[self.time_scale]
