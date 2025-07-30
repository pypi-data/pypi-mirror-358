"""Adapter for LangMem backend"""

from __future__ import annotations

from typing import List

from ..core import MemoryEvent, MemoryStore


class LangMemStore(MemoryStore):
    def __init__(self, **kwargs) -> None:
        try:
            import langmem  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "langmem is not installed. `pip install langmem` or add the `langmem` extra."
            ) from exc

        # LangMem provides a Memory object (per docs). We'll fallback to simple wrapper
        self._client = kwargs.get("client") or getattr(langmem, "Memory", None)()
        if self._client is None:
            raise RuntimeError(
                "Could not instantiate LangMem Memory client. Check API changes."
            )

    def add(self, event: MemoryEvent) -> None:
        # LangMem expects dict-like records
        self._client.add(
            sender=event.sender, content=event.content, metadata=event.metadata
        )

    def query(self, query: str, limit: int = 5) -> List[MemoryEvent]:
        # LangMem exposes search that returns list of dicts w/ content
        hits = self._client.search(query=query, top_k=limit)
        results: List[MemoryEvent] = []
        for h in hits:
            results.append(
                MemoryEvent(
                    sender=h.get("sender", "unknown"),
                    content=h["content"],
                    metadata=h.get("metadata", {}),
                    timestamp=h.get("timestamp") or None,  # type: ignore
                )
            )
        return results

    def clear(self) -> None:
        self._client.clear()
