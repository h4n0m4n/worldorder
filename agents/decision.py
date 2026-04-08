"""Decision framework — structured decision-making for leader agents."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    DIPLOMACY = "diplomacy"
    MILITARY = "military"
    ECONOMIC = "economic"
    INTELLIGENCE = "intelligence"
    TRADE = "trade"
    ALLIANCE = "alliance"
    SANCTION = "sanction"
    AID = "aid"
    DOMESTIC_POLICY = "domestic_policy"
    PROPAGANDA = "propaganda"
    NEGOTIATE = "negotiate"
    THREATEN = "threaten"
    CONCEDE = "concede"
    STALL = "stall"
    NO_ACTION = "no_action"


class Mood(str, Enum):
    CONFIDENT = "confident"
    ANXIOUS = "anxious"
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    OPPORTUNISTIC = "opportunistic"
    DESPERATE = "desperate"


class Action(BaseModel):
    type: ActionType
    target: str  # country code or "global"
    detail: str
    intensity: float = 0.5  # 0-1

    def __str__(self) -> str:
        return f"{self.type.value} → {self.target}: {self.detail} (intensity: {self.intensity:.1f})"


class LeaderDecision(BaseModel):
    leader_id: str
    country_code: str
    turn: int
    year: int
    inner_thoughts: str = ""
    public_statement: str = ""
    actions: list[Action] = Field(default_factory=list)
    mood: Mood = Mood.CONFIDENT

    @classmethod
    def from_llm_output(
        cls,
        raw: dict[str, Any],
        leader_id: str,
        country_code: str,
        turn: int,
        year: int,
    ) -> LeaderDecision:
        actions = []
        for a in raw.get("actions", []):
            try:
                actions.append(Action(
                    type=ActionType(a.get("type", "no_action")),
                    target=a.get("target", "global"),
                    detail=a.get("detail", ""),
                    intensity=float(a.get("intensity", 0.5)),
                ))
            except (ValueError, KeyError):
                continue

        try:
            mood = Mood(raw.get("mood", "confident"))
        except ValueError:
            mood = Mood.CONFIDENT

        return cls(
            leader_id=leader_id,
            country_code=country_code,
            turn=turn,
            year=year,
            inner_thoughts=raw.get("inner_thoughts", ""),
            public_statement=raw.get("public_statement", ""),
            actions=actions,
            mood=mood,
        )

    def has_military_action(self) -> bool:
        return any(a.type in (ActionType.MILITARY, ActionType.THREATEN) for a in self.actions)

    def has_diplomatic_action(self) -> bool:
        return any(
            a.type in (ActionType.DIPLOMACY, ActionType.NEGOTIATE, ActionType.ALLIANCE, ActionType.CONCEDE)
            for a in self.actions
        )

    def max_intensity(self) -> float:
        if not self.actions:
            return 0.0
        return max(a.intensity for a in self.actions)

    def targets(self) -> set[str]:
        return {a.target for a in self.actions if a.target != "global"}
