"""
LangMem adapter for phoenix‑ai‑memory – fixed KeyError '__pregel_store'

Requires:
  pip install langmem langgraph
"""
from __future__ import annotations

from typing import List

from langgraph.config import configure  # 🆕 register store globally
from langgraph.store.memory import InMemoryStore
from langmem import create_memory_manager, create_search_memory_tool

from ..core import MemoryEvent, MemoryStore


class LangMemStore(MemoryStore):
    def __init__(
        self,
        model: str = "openai:gpt-4o-mini",
        namespace: tuple[str, ...] = ("memories",),
        store: InMemoryStore | None = None,
        **llm_kwargs,
    ):
        # 1️⃣  Create or accept a vector store
        self._store = store or InMemoryStore(
            index={"dims": 1536, "embed": "openai:text-embedding-3-small"}
        )

        # 2️⃣  Tell LangGraph THIS is the default store  (fixes KeyError)
        configure(store=self._store)                                   # ★

        # 3️⃣  Build writer & reader — pass model POSITIONALLY (PEP 570)
        self._manager = create_memory_manager(
            model,                                                     # positional‑only
            instructions="Extract and store important user facts.",
            enable_inserts=True,
            **llm_kwargs,
        ).bind(store=self._store)

        self._search = create_search_memory_tool(namespace=namespace).bind(
            store=self._store
        )

    # ---------- MemoryStore interface ----------
    def add(self, event: MemoryEvent) -> None:
        self._manager.invoke({
            "messages": [{"role": event.sender, "content": event.content}]
        })

    def query(self, query: str, limit: int = 5) -> List[MemoryEvent]:
        hits = self._search.invoke({"query": query, "k": limit})
        return [
            MemoryEvent(
                sender   = h.get("role", "assistant"),
                content  = h["content"],
                metadata = h.get("metadata", {}),
                timestamp= h.get("created_at"),
            )
            for h in hits
        ]

    def clear(self) -> None:
        self._store.reset()
