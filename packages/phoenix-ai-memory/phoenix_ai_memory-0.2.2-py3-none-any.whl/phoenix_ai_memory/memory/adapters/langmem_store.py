"""
Adapter for LangMem ≥ 0.0.24

LangMem exposes `create_memory_manager` for extraction/upsert and a
`create_search_memory_tool` for retrieval.  We wire those together so
the store looks just like any other `MemoryStore`.
"""

from __future__ import annotations

from typing import List

from ..core import MemoryEvent, MemoryStore


class LangMemStore(MemoryStore):
    def __init__(
        self,
        model: str = "anthropic:claude-3-5-sonnet-latest",
        namespace: tuple[str, ...] = ("memories",),
        **kwargs,
    ) -> None:
        try:
            from langmem import (create_memory_manager,  # type: ignore
                                 create_search_memory_tool)
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "LangMem is not installed — `pip install langmem`."
            ) from exc

        # One manager for writes …
        self._manager = create_memory_manager(
            model,
            instructions="Extract and store all user facts, preferences and important events.",
            enable_inserts=True,
            **kwargs,
        )
        # … one tool for reads
        self._search = create_search_memory_tool(namespace=namespace)

        # LangMem expects a `store` instance that implements BaseStore.
        # For quick starts we use the built‑in in‑memory store; users can
        # inject their own via **kwargs.
        if "store" in kwargs:
            self._store = kwargs["store"]  # external store
        else:
            from langgraph.store.memory import \
                InMemoryStore  # lightweight vector store

            self._store = InMemoryStore(
                index={"dims": 1536, "embed": "openai:text-embedding-3-small"}
            )

        # Bind tools → store
        self._manager = self._manager.bind(store=self._store)
        self._search = self._search.bind(store=self._store)

    # ---------- MemoryStore interface ----------
    def add(self, event: MemoryEvent) -> None:
        """Write a single chat turn to LangMem; LangMem decides what to keep."""
        conversation = [{"role": event.sender, "content": event.content}]
        self._manager.invoke({"messages": conversation})

    def query(self, query: str, limit: int = 5) -> List[MemoryEvent]:
        hits = self._search.invoke({"query": query, "k": limit})
        # Each hit is a dict with 'role', 'content', 'metadata', 'created_at'
        out: List[MemoryEvent] = []
        for h in hits:
            out.append(
                MemoryEvent(
                    sender=h.get("role", "assistant"),
                    content=h["content"],
                    metadata=h.get("metadata", {}),
                    timestamp=h.get("created_at"),
                )
            )
        return out

    def clear(self) -> None:
        # In‑memory store: wipe vector index
        self._store.reset()
