"""Ollama provider — fully local, fully free."""

from __future__ import annotations

from typing import Any

import httpx

from llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(
        self,
        model: str = "llama3.1",
        base_url: str = "http://localhost:11434",
        timeout: float = 120.0,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def generate(self, prompt: str, system: str = "") -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            return resp.json()["response"]

    async def generate_structured(
        self, prompt: str, schema: dict[str, Any], system: str = ""
    ) -> dict[str, Any]:
        schema_hint = (
            "Respond ONLY with a valid JSON object. No markdown fences, no explanation.\n"
            "Required keys: inner_thoughts (string), public_statement (string), "
            "actions (array of {type, target, detail, intensity}), mood (string).\n"
            "Example: {\"inner_thoughts\":\"...\",\"public_statement\":\"...\","
            "\"actions\":[{\"type\":\"diplomacy\",\"target\":\"US\",\"detail\":\"...\",\"intensity\":0.5}],"
            "\"mood\":\"confident\"}"
        )
        full_system = f"{system}\n\n{schema_hint}" if system else schema_hint

        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "system": full_system,
            "stream": False,
            "format": "json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            raw = resp.json()["response"]

        return self._extract_json(raw)

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
