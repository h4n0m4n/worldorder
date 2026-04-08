"""Central event bus — every simulation event flows through here.

Events cascade: War → Oil price spike → Inflation → Civil unrest.
All events are logged for replay / rewind.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Awaitable

from pydantic import BaseModel, Field


class EventCategory(str, Enum):
    MILITARY = "military"
    ECONOMIC = "economic"
    DIPLOMATIC = "diplomatic"
    POLITICAL = "political"
    SOCIAL = "social"
    TECHNOLOGICAL = "technological"
    ENVIRONMENTAL = "environmental"
    CULTURAL = "cultural"
    INTELLIGENCE = "intelligence"
    CRISIS = "crisis"


class EventSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SimEvent(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    turn: int
    year: int
    category: EventCategory
    severity: EventSeverity = EventSeverity.MEDIUM
    title: str
    description: str
    source_country: str | None = None
    target_countries: list[str] = Field(default_factory=list)
    effects: dict[str, Any] = Field(default_factory=dict)
    triggered_by: str | None = None  # parent event id
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def __str__(self) -> str:
        sev = self.severity.value.upper()
        return f"[{sev}] {self.title} (turn {self.turn}, {self.year})"


EventHandler = Callable[[SimEvent], Awaitable[None]]


class EventBus:
    """Publish / subscribe event system with full history."""

    def __init__(self) -> None:
        self._handlers: dict[EventCategory | None, list[EventHandler]] = {}
        self._history: list[SimEvent] = []

    def subscribe(
        self,
        handler: EventHandler,
        category: EventCategory | None = None,
    ) -> None:
        self._handlers.setdefault(category, []).append(handler)

    async def publish(self, event: SimEvent) -> None:
        self._history.append(event)
        for handler in self._handlers.get(event.category, []):
            await handler(event)
        for handler in self._handlers.get(None, []):  # wildcard subscribers
            await handler(event)

    def history(self, category: EventCategory | None = None, last_n: int | None = None) -> list[SimEvent]:
        events = self._history
        if category:
            events = [e for e in events if e.category == category]
        if last_n:
            events = events[-last_n:]
        return events

    def clear(self) -> None:
        self._history.clear()

    @property
    def total_events(self) -> int:
        return len(self._history)
