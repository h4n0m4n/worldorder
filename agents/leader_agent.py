"""Leader Agent — the core AI agent representing a world leader.

Combines personality, memory, civilization DNA, and advisor input
to make strategic decisions each turn.
"""

from __future__ import annotations

import uuid
from typing import Any

from agents.base_agent import BaseAgent
from agents.memory import MemoryStore, MemoryEntry
from agents.civilization_dna import CivilizationDNA
from agents.advisor_agent import AdvisorPanel, AdvisorAdvice
from agents.decision import LeaderDecision, Action
from engine.world_state import CountryState
from engine.event_bus import SimEvent
from llm.base import LLMProvider
from llm.prompt_builder import (
    build_leader_system_prompt,
    build_turn_prompt,
    build_world_summary,
    DECISION_SCHEMA,
)


class LeaderAgent(BaseAgent):
    """Full-featured leader agent with memory, advisors, and civilization DNA."""

    def __init__(
        self,
        leader_profile: dict[str, Any],
        country: CountryState,
        llm: LLMProvider,
        civilization_dna: CivilizationDNA | None = None,
        use_advisors: bool = True,
        use_vector_memory: bool = False,
    ) -> None:
        super().__init__(
            agent_id=leader_profile.get("id", "unknown"),
            name=leader_profile.get("name", "Unknown Leader"),
            llm=llm,
        )
        self.profile = leader_profile
        self.country = country
        self.dna = civilization_dna
        self.memory = MemoryStore(
            owner_id=self.agent_id,
            use_vector_db=use_vector_memory,
        )
        self.advisor_panel: AdvisorPanel | None = None
        if use_advisors:
            self.advisor_panel = AdvisorPanel(country.code, llm)
        self.decisions_history: list[LeaderDecision] = []

    def _build_system_prompt(self) -> str:
        base = build_leader_system_prompt(self.profile, self.country)
        if self.dna:
            base += f"\n\n{self.dna.to_prompt_section()}"
        return base

    async def make_decision(
        self,
        turn: int,
        year: int,
        recent_events: list[SimEvent],
        all_countries: list[CountryState],
    ) -> LeaderDecision:
        """Full decision pipeline: memory → advisors → think → decide."""

        world_summary = build_world_summary(all_countries)

        # 1. Recall relevant memories
        event_text = " ".join(e.title for e in recent_events)
        memory_context = self.memory.build_context(query=event_text)

        # 2. Get advisor input (if enabled)
        advisor_text = ""
        if self.advisor_panel:
            situation = (
                f"Year {year}, Turn {turn}.\n"
                f"Recent events: {event_text}\n"
                f"Country status: GDP ${self.country.economy.gdp_trillion:.1f}T, "
                f"Stability {self.country.domestic.stability:.0%}, "
                f"Military {self.country.military.power_index:.0%}\n"
                f"{world_summary}"
            )
            advice_list = await self.advisor_panel.get_all_advice(situation)
            advisor_text = self.advisor_panel.format_advice_for_leader(advice_list)

        # 3. Build prompts
        system_prompt = self._build_system_prompt()
        if advisor_text:
            system_prompt += f"\n\n{advisor_text}"

        turn_prompt = build_turn_prompt(
            turn=turn,
            year=year,
            recent_events=recent_events,
            world_summary=world_summary,
            memory_context=memory_context,
        )

        # 4. Get LLM decision
        try:
            raw = await self.llm.generate_structured(
                prompt=turn_prompt,
                schema=DECISION_SCHEMA,
                system=system_prompt,
            )
        except Exception as e:
            raw = {
                "inner_thoughts": f"[Decision error: {e}]",
                "public_statement": "We are monitoring the situation closely.",
                "actions": [{"type": "stall", "target": "global", "detail": "Awaiting developments"}],
                "mood": "anxious",
            }

        decision = LeaderDecision.from_llm_output(
            raw=raw,
            leader_id=self.agent_id,
            country_code=self.country.code,
            turn=turn,
            year=year,
        )

        # 5. Store in memory
        self._store_decision_memory(decision, recent_events)
        self.decisions_history.append(decision)

        return decision

    def _store_decision_memory(
        self,
        decision: LeaderDecision,
        events: list[SimEvent],
    ) -> None:
        """Store this turn's events and decision in memory."""
        for event in events:
            importance = {"low": 0.2, "medium": 0.4, "high": 0.7, "critical": 1.0}.get(
                event.severity.value, 0.4
            )
            emotion = None
            if event.source_country and event.source_country != self.country.code:
                if event.category.value == "military":
                    emotion = "fear" if self.country.code in event.target_countries else "anger"
                elif event.category.value == "diplomatic":
                    emotion = "trust"

            self.memory.add(MemoryEntry(
                id=f"event_{event.id}",
                turn=decision.turn,
                year=decision.year,
                category="episodic",
                content=f"{event.title}: {event.description}",
                importance=importance,
                related_countries=event.target_countries + (
                    [event.source_country] if event.source_country else []
                ),
                emotion=emotion,
            ))

        if decision.inner_thoughts:
            self.memory.add(MemoryEntry(
                id=f"thought_{uuid.uuid4().hex[:8]}",
                turn=decision.turn,
                year=decision.year,
                category="semantic",
                content=f"My thinking: {decision.inner_thoughts[:300]}",
                importance=0.3,
            ))

        for action in decision.actions:
            if action.intensity >= 0.7:
                self.memory.add(MemoryEntry(
                    id=f"action_{uuid.uuid4().hex[:8]}",
                    turn=decision.turn,
                    year=decision.year,
                    category="episodic",
                    content=f"I took action: {action}",
                    importance=action.intensity,
                    related_countries=[action.target] if action.target != "global" else [],
                ))

    def get_relationship_summary(self) -> dict[str, str]:
        """Summarize this leader's view of relationships based on memory."""
        summary: dict[str, str] = {}
        relationships = self.profile.get("relationships", {})
        for code, rel in relationships.items():
            memories = self.memory.recall_by_country(code, n=3)
            if memories:
                recent_emotion = memories[0].emotion or "neutral"
                summary[code] = f"{rel} (recent: {recent_emotion})"
            else:
                summary[code] = str(rel)
        return summary
