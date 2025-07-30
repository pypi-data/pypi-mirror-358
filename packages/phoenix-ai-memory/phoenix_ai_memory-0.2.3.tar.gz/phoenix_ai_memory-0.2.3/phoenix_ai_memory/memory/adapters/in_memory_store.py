"""Simple in‑process store for testing"""

from __future__ import annotations

from typing import List

from ..core import MemoryEvent, MemoryStore


class InMemoryStore(MemoryStore):
    """Stores events in a list and performs naive keyword search"""

    def __init__(self) -> None:
        self._events: List[MemoryEvent] = []

    def add(self, event: MemoryEvent) -> None:
        self._events.append(event)

    def query(self, query: str, limit: int = 5) -> List[MemoryEvent]:
        q_words = set(query.lower().split())
        scored = []
        for e in self._events:
            score = len(q_words & set(e.content.lower().split()))
            scored.append((score, e))
        scored.sort(key=lambda t: t[0], reverse=True)
        return [e for _, e in scored[:limit]]

    def clear(self) -> None:
        self._events.clear()
