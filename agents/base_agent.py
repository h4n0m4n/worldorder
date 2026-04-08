"""Base agent class — shared logic for all AI agents."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field

from llm.base import LLMProvider


class AgentMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class BaseAgent:
    """Abstract base for all simulation agents (leaders, advisors, etc.)."""

    def __init__(
        self,
        agent_id: str | None = None,
        name: str = "Agent",
        llm: LLMProvider | None = None,
    ) -> None:
        self.agent_id = agent_id or uuid.uuid4().hex[:8]
        self.name = name
        self.llm = llm
        self.conversation_history: list[AgentMessage] = []

    def set_llm(self, llm: LLMProvider) -> None:
        self.llm = llm

    def add_message(self, role: str, content: str, **metadata: Any) -> None:
        self.conversation_history.append(
            AgentMessage(role=role, content=content, metadata=metadata)
        )

    def get_context_window(self, max_messages: int = 20) -> list[dict[str, str]]:
        """Return recent conversation as list of dicts for LLM."""
        return [
            {"role": m.role, "content": m.content}
            for m in self.conversation_history[-max_messages:]
        ]

    async def think(self, prompt: str, system: str = "") -> str:
        """Generate a free-form response."""
        if not self.llm:
            raise RuntimeError(f"Agent {self.name} has no LLM provider set.")
        self.add_message("user", prompt)
        response = await self.llm.generate(prompt, system=system)
        self.add_message("assistant", response)
        return response

    async def decide(self, prompt: str, schema: dict[str, Any], system: str = "") -> dict[str, Any]:
        """Generate a structured JSON decision."""
        if not self.llm:
            raise RuntimeError(f"Agent {self.name} has no LLM provider set.")
        self.add_message("user", prompt)
        result = await self.llm.generate_structured(prompt, schema, system=system)
        self.add_message("assistant", str(result))
        return result

    def reset(self) -> None:
        self.conversation_history.clear()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.agent_id} name={self.name}>"
