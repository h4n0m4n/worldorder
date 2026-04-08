"""Groq provider — extremely fast, free tier available."""

from __future__ import annotations

import os
from typing import Any

import httpx

from llm.base import LLMProvider


class GroqProvider(LLMProvider):
    name = "groq"

    def __init__(
        self,
        model: str = "llama-3.1-8b-instant",
        api_key: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1"
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate(self, prompt: str, system: str = "") -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json={"model": self.model, "messages": messages, "temperature": 0.7},
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def generate_structured(
        self, prompt: str, schema: dict[str, Any], system: str = ""
    ) -> dict[str, Any]:
        schema_hint = (
            "You MUST respond with valid JSON matching this schema. "
            "No markdown, no explanation, ONLY the JSON object.\n\n"
            f"Schema: {schema}"
        )
        full_system = f"{system}\n\n{schema_hint}" if system else schema_hint
        raw = await self.generate(prompt, system=full_system)
        return self._extract_json(raw)
