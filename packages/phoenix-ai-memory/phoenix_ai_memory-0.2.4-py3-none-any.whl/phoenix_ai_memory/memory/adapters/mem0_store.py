"""Adapter for Mem0 memory"""

from __future__ import annotations

from typing import List

from ..core import MemoryEvent, MemoryStore


class Mem0Store(MemoryStore):
    def __init__(self, **kwargs) -> None:
        try:
            from mem0 import Memory as Mem0Memory  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "mem0 is not installed. `pip install mem0` or add the `mem0` extra."
            ) from exc
        # Mem0 requires an LLM client; user can pass one
        client = kwargs.get("client")
        self._memory = (
            Mem0Memory(client=client, **kwargs) if client else Mem0Memory(**kwargs)
        )

    def add(self, event: MemoryEvent) -> None:
        self._memory.write(
            sender=event.sender, content=event.content, metadata=event.metadata
        )

    def query(self, query: str, limit: int = 5) -> List[MemoryEvent]:
        results = self._memory.search(query=query, k=limit)
        mem_events: List[MemoryEvent] = []
        for r in results:
            mem_events.append(
                MemoryEvent(
                    sender=r.get("sender", "user"),
                    content=r["content"],
                    metadata=r.get("metadata", {}),
                    timestamp=r.get("timestamp"),
                )
            )
        return mem_events

    def clear(self) -> None:
        self._memory.clear()
