"""Memory system — episodic, semantic, and emotional memory for agents.

Uses ChromaDB for vector search when available, falls back to simple in-memory store.
"""

from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    id: str
    timestamp: float = Field(default_factory=time.time)
    turn: int
    year: int
    category: str  # episodic, semantic, emotional
    content: str
    importance: float = 0.5  # 0-1
    related_countries: list[str] = Field(default_factory=list)
    emotion: str | None = None  # trust, fear, anger, gratitude, betrayal
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryStore:
    """In-memory store with importance-weighted retrieval.

    ChromaDB integration is optional — when installed, memories are also
    persisted to a vector collection for semantic search.
    """

    def __init__(self, owner_id: str, use_vector_db: bool = False) -> None:
        self.owner_id = owner_id
        self._entries: list[MemoryEntry] = []
        self._chroma_collection = None

        if use_vector_db:
            self._init_chroma()

    def _init_chroma(self) -> None:
        try:
            import chromadb
            client = chromadb.Client()
            self._chroma_collection = client.get_or_create_collection(
                name=f"memory_{self.owner_id}"
            )
        except ImportError:
            pass

    def add(self, entry: MemoryEntry) -> None:
        self._entries.append(entry)
        if self._chroma_collection is not None:
            self._chroma_collection.add(
                ids=[entry.id],
                documents=[entry.content],
                metadatas=[{
                    "turn": entry.turn,
                    "year": entry.year,
                    "category": entry.category,
                    "importance": entry.importance,
                    "emotion": entry.emotion or "",
                }],
            )

    def recall_recent(self, n: int = 10) -> list[MemoryEntry]:
        return sorted(self._entries, key=lambda e: e.timestamp, reverse=True)[:n]

    def recall_important(self, n: int = 10) -> list[MemoryEntry]:
        return sorted(self._entries, key=lambda e: e.importance, reverse=True)[:n]

    def recall_by_country(self, country_code: str, n: int = 10) -> list[MemoryEntry]:
        relevant = [e for e in self._entries if country_code in e.related_countries]
        return sorted(relevant, key=lambda e: e.importance, reverse=True)[:n]

    def recall_emotional(self, emotion: str, n: int = 10) -> list[MemoryEntry]:
        relevant = [e for e in self._entries if e.emotion == emotion]
        return sorted(relevant, key=lambda e: e.importance, reverse=True)[:n]

    def recall_grudges(self) -> list[MemoryEntry]:
        return self.recall_emotional("betrayal") + self.recall_emotional("anger")

    def recall_alliances(self) -> list[MemoryEntry]:
        return self.recall_emotional("trust") + self.recall_emotional("gratitude")

    def search(self, query: str, n: int = 5) -> list[MemoryEntry]:
        """Semantic search via ChromaDB, or keyword fallback."""
        if self._chroma_collection is not None:
            results = self._chroma_collection.query(query_texts=[query], n_results=n)
            found_ids = set(results["ids"][0]) if results["ids"] else set()
            return [e for e in self._entries if e.id in found_ids]

        query_lower = query.lower()
        scored = []
        for e in self._entries:
            score = 0.0
            if query_lower in e.content.lower():
                score += 1.0
            score += e.importance * 0.5
            scored.append((score, e))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored[:n]]

    def build_context(self, query: str = "", max_entries: int = 15) -> str:
        """Build a text summary of relevant memories for the LLM prompt."""
        entries: list[MemoryEntry] = []

        if query:
            entries.extend(self.search(query, n=5))

        important = self.recall_important(5)
        recent = self.recall_recent(5)

        seen_ids = {e.id for e in entries}
        for e in important + recent:
            if e.id not in seen_ids:
                entries.append(e)
                seen_ids.add(e.id)

        entries = entries[:max_entries]
        if not entries:
            return ""

        lines = ["KEY MEMORIES:"]
        for e in entries:
            emotion_tag = f" [{e.emotion}]" if e.emotion else ""
            lines.append(
                f"  - (Year {e.year}, importance {e.importance:.1f}{emotion_tag}) {e.content}"
            )
        return "\n".join(lines)

    @property
    def size(self) -> int:
        return len(self._entries)
