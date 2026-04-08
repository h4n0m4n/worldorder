"""Time Engine — manages simulation clock, speed, and era transitions."""

from __future__ import annotations

from engine.config import Era, TimeScale, SimulationConfig
from engine.world_state import WorldState
from engine.event_bus import EventBus, SimEvent, EventCategory, EventSeverity


ERA_RANGES: dict[Era, tuple[int, int]] = {
    Era.ANCIENT: (-3000, 500),
    Era.MEDIEVAL: (500, 1500),
    Era.EARLY_MODERN: (1500, 1800),
    Era.MODERN: (1800, 2000),
    Era.CONTEMPORARY: (2000, 2030),
    Era.FUTURE: (2030, 2100),
}


class TimeEngine:
    """Drives the simulation forward turn by turn."""

    def __init__(
        self,
        config: SimulationConfig,
        world: WorldState,
        event_bus: EventBus,
    ) -> None:
        self.config = config
        self.world = world
        self.event_bus = event_bus
        self.world.year = config.start_year
        self.finished = False

    @property
    def current_era(self) -> Era:
        for era, (lo, hi) in ERA_RANGES.items():
            if lo <= self.world.year < hi:
                return era
        return Era.FUTURE

    @property
    def years_per_turn(self) -> int:
        return {
            TimeScale.DECADE: 10,
            TimeScale.YEAR: 1,
            TimeScale.MONTH: 1,  # sub-year handled separately
        }[self.config.time_scale]

    async def tick(self) -> bool:
        """Advance one turn. Returns False when simulation ends."""
        if self.finished:
            return False

        self.world.apply_economic_tick()
        self.world.apply_population_tick()
        self.world.advance_turn(years=self.years_per_turn)

        if self.world.year >= self.config.end_year or self.world.turn >= self.config.max_turns:
            self.finished = True
            await self.event_bus.publish(SimEvent(
                turn=self.world.turn,
                year=self.world.year,
                category=EventCategory.POLITICAL,
                severity=EventSeverity.CRITICAL,
                title="Simulation Complete",
                description=f"The simulation has reached its end at year {self.world.year}.",
            ))
            return False

        era_now = self.current_era
        if era_now != self.config.era:
            await self.event_bus.publish(SimEvent(
                turn=self.world.turn,
                year=self.world.year,
                category=EventCategory.POLITICAL,
                severity=EventSeverity.HIGH,
                title=f"Era Transition → {era_now.value.replace('_', ' ').title()}",
                description=f"The world has entered the {era_now.value} era.",
            ))
            self.config.era = era_now

        return True
