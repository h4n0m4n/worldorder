"""LLM provider registry — pick your backend at runtime."""

from __future__ import annotations

from llm.base import LLMProvider
from llm.ollama import OllamaProvider
from llm.groq import GroqProvider
from llm.openrouter import OpenRouterProvider
from llm.openai_provider import OpenAIProvider


_PROVIDERS: dict[str, type[LLMProvider]] = {
    "ollama": OllamaProvider,
    "groq": GroqProvider,
    "openrouter": OpenRouterProvider,
    "openai": OpenAIProvider,
}


def get_provider(name: str, **kwargs) -> LLMProvider:
    cls = _PROVIDERS.get(name)
    if cls is None:
        available = ", ".join(_PROVIDERS)
        raise ValueError(f"Unknown LLM provider '{name}'. Available: {available}")
    return cls(**kwargs)


def register_provider(name: str, cls: type[LLMProvider]) -> None:
    _PROVIDERS[name] = cls


def available_providers() -> list[str]:
    return list(_PROVIDERS.keys())
