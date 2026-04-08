"""Advisor agents — each leader has specialized advisors who offer perspectives.

The leader may listen or ignore them based on personality.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from agents.base_agent import BaseAgent
from llm.base import LLMProvider


class AdvisorRole(str, Enum):
    MILITARY = "military"
    ECONOMIC = "economic"
    INTELLIGENCE = "intelligence"
    DIPLOMATIC = "diplomatic"
    DOMESTIC = "domestic"


ADVISOR_SYSTEM_PROMPTS: dict[AdvisorRole, str] = {
    AdvisorRole.MILITARY: (
        "You are a military advisor. Assess threats, recommend force posture, "
        "evaluate military options. Be direct about capabilities and risks. "
        "Think in terms of deterrence, escalation ladders, and force projection."
    ),
    AdvisorRole.ECONOMIC: (
        "You are an economic advisor. Analyze fiscal health, trade impacts, "
        "sanctions effects, and economic leverage. Recommend policies that "
        "strengthen economic position. Consider both short and long-term impacts."
    ),
    AdvisorRole.INTELLIGENCE: (
        "You are an intelligence advisor. Assess hidden intentions of other leaders, "
        "identify covert threats and opportunities, recommend intelligence operations. "
        "Be paranoid but analytical. Trust no one fully."
    ),
    AdvisorRole.DIPLOMATIC: (
        "You are a diplomatic advisor. Identify alliance opportunities, "
        "recommend negotiation strategies, assess international opinion. "
        "Think about coalitions, leverage, and face-saving compromises."
    ),
    AdvisorRole.DOMESTIC: (
        "You are a domestic affairs advisor. Assess public opinion, internal stability, "
        "opposition movements, and social pressures. Recommend policies that maintain "
        "regime stability and popular support."
    ),
}

ADVISOR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "assessment": {"type": "string", "description": "Brief situation assessment from your domain"},
        "recommendation": {"type": "string", "description": "Your recommended course of action"},
        "risk_level": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "dissent": {"type": "boolean", "description": "Do you disagree with the current direction?"},
    },
    "required": ["assessment", "recommendation", "risk_level", "confidence"],
}


class AdvisorAdvice(BaseModel):
    role: AdvisorRole
    assessment: str = ""
    recommendation: str = ""
    risk_level: str = "medium"
    confidence: float = 0.5
    dissent: bool = False


class AdvisorAgent(BaseAgent):
    """A specialized advisor that provides domain-specific counsel."""

    def __init__(
        self,
        role: AdvisorRole,
        country_code: str,
        llm: LLMProvider | None = None,
        hawkishness: float = 0.5,  # 0=dove, 1=hawk
    ) -> None:
        super().__init__(
            agent_id=f"advisor_{role.value}_{country_code}",
            name=f"{role.value.title()} Advisor ({country_code})",
            llm=llm,
        )
        self.role = role
        self.country_code = country_code
        self.hawkishness = hawkishness

    def system_prompt(self) -> str:
        base = ADVISOR_SYSTEM_PROMPTS[self.role]
        hawk_note = ""
        if self.hawkishness > 0.7:
            hawk_note = "\nYou tend toward aggressive, hawkish recommendations."
        elif self.hawkishness < 0.3:
            hawk_note = "\nYou tend toward cautious, dovish recommendations."
        return f"{base}{hawk_note}\nRespond ONLY with JSON. No other text."

    async def advise(self, situation: str) -> AdvisorAdvice:
        """Generate advice for the current situation."""
        try:
            raw = await self.decide(
                prompt=situation,
                schema=ADVISOR_SCHEMA,
                system=self.system_prompt(),
            )
            return AdvisorAdvice(
                role=self.role,
                assessment=raw.get("assessment", ""),
                recommendation=raw.get("recommendation", ""),
                risk_level=raw.get("risk_level", "medium"),
                confidence=float(raw.get("confidence", 0.5)),
                dissent=bool(raw.get("dissent", False)),
            )
        except Exception as e:
            return AdvisorAdvice(
                role=self.role,
                assessment=f"[Advisor unavailable: {e}]",
                recommendation="Maintain current course.",
                risk_level="medium",
                confidence=0.3,
            )


class AdvisorPanel:
    """A panel of advisors for a single leader."""

    def __init__(self, country_code: str, llm: LLMProvider | None = None) -> None:
        self.country_code = country_code
        self.advisors: dict[AdvisorRole, AdvisorAgent] = {}
        if llm:
            self.create_default_panel(llm)

    def create_default_panel(self, llm: LLMProvider) -> None:
        for role in AdvisorRole:
            self.advisors[role] = AdvisorAgent(
                role=role,
                country_code=self.country_code,
                llm=llm,
            )

    def set_hawkishness(self, role: AdvisorRole, value: float) -> None:
        if role in self.advisors:
            self.advisors[role].hawkishness = value

    async def get_all_advice(self, situation: str) -> list[AdvisorAdvice]:
        """Gather advice from all advisors."""
        import asyncio
        tasks = [advisor.advise(situation) for advisor in self.advisors.values()]
        return list(await asyncio.gather(*tasks))

    def format_advice_for_leader(self, advice_list: list[AdvisorAdvice]) -> str:
        """Format advisor input as text for the leader's prompt."""
        if not advice_list:
            return ""
        lines = ["YOUR ADVISORS' INPUT:"]
        for adv in advice_list:
            dissent_marker = " [DISSENT]" if adv.dissent else ""
            lines.append(
                f"  [{adv.role.value.upper()} ADVISOR]{dissent_marker} "
                f"(confidence: {adv.confidence:.0%}, risk: {adv.risk_level})\n"
                f"    Assessment: {adv.assessment}\n"
                f"    Recommendation: {adv.recommendation}"
            )
        return "\n".join(lines)
