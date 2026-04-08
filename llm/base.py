"""LLM Provider interface — pluggable adapter pattern."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Base class every LLM backend must implement."""

    name: str = "base"

    @abstractmethod
    async def generate(self, prompt: str, system: str = "") -> str:
        """Return free-form text completion."""
        ...

    @abstractmethod
    async def generate_structured(
        self, prompt: str, schema: dict[str, Any], system: str = ""
    ) -> dict[str, Any]:
        """Return a JSON object matching *schema*."""
        ...

    async def health_check(self) -> bool:
        """Quick connectivity test."""
        try:
            resp = await self.generate("Say OK.", system="Respond with one word.")
            return len(resp.strip()) > 0
        except Exception:
            return False

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        """Best-effort JSON extraction from LLM output."""
        text = text.strip()
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # Try to find JSON block in markdown fences
        for start_tok in ("```json", "```"):
            if start_tok in text:
                start = text.index(start_tok) + len(start_tok)
                end = text.index("```", start)
                return json.loads(text[start:end].strip())
        # Last resort: find first { ... }
        brace_start = text.find("{")
        brace_end = text.rfind("}") + 1
        if brace_start != -1 and brace_end > brace_start:
            return json.loads(text[brace_start:brace_end])
        raise ValueError(f"Could not extract JSON from LLM output: {text[:200]}")
