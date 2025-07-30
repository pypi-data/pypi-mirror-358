"""
Memory façade and backend registry
"""

from __future__ import annotations

import importlib
import json  # ✅  fix NameError
import os
from typing import Dict, Type

from .adapters.in_memory_store import InMemoryStore
from .core import MemoryEvent, MemoryPolicy, MemoryStore
from .policies.basic import BasicPolicy

# ---------------------------------------------------------------------------
# Registry ------------------------------------------------------------------
# ---------------------------------------------------------------------------
_DEFAULT_REGISTRY: Dict[str, Type[MemoryStore]] = {
    "in_memory": InMemoryStore,
}

for _name, _path in {
    "langmem": "phoenix_ai_memory.memory.adapters.langmem_store:LangMemStore",
    "zep":     "phoenix_ai_memory.memory.adapters.zep_store:ZepStore",
    "mem0":    "phoenix_ai_memory.memory.adapters.mem0_store:Mem0Store",
}.items():
    try:
        mod, attr = _path.split(":")
        _DEFAULT_REGISTRY[_name] = getattr(importlib.import_module(mod), attr)
    except Exception:
        # Missing optional dependency: leave backend unregistered
        pass

# ---------------------------------------------------------------------------
# Public façade -------------------------------------------------------------
# ---------------------------------------------------------------------------
class Memory:
    def __init__(
        self,
        store:   MemoryStore  | None = None,
        policy:  MemoryPolicy | None = None,
        retrieval_k: int = 5,
    ) -> None:
        self.store        = store   or InMemoryStore()
        self.policy       = policy  or BasicPolicy()
        self.retrieval_k  = retrieval_k

    # ---------- factory helper --------------------------------------------
    @classmethod
    def from_env(cls) -> "Memory":
        backend      = os.getenv("PHOENIX_BACKEND", "in_memory")
        retrieval_k  = int(os.getenv("PHOENIX_RETRIEVAL_K", "5"))
        policy_name  = os.getenv("PHOENIX_POLICY", "basic")
        store_kwargs = json.loads(os.getenv("PHOENIX_STORE_KWARGS", "{}"))

        # 1️⃣  resolve the backend class (dynamic import if needed)
        store_cls: Type[MemoryStore] | None = _DEFAULT_REGISTRY.get(backend)
        if store_cls is None:
            try:
                mod, attr = backend.split(":")
                store_cls = getattr(importlib.import_module(mod), attr)
            except Exception as exc:
                raise ValueError(f"Unknown backend '{backend}': {exc}") from exc

        # 2️⃣  construct the store exactly ONCE, passing kwargs
        store = store_cls(**store_kwargs)

        # 3️⃣  choose policy (placeholder for future custom policies)
        policy = BasicPolicy() if policy_name == "basic" else BasicPolicy()

        return cls(store=store, policy=policy, retrieval_k=retrieval_k)

    # ---------- high‑level API --------------------------------------------
    def remember(self, sender: str, content: str, **meta):
        event = MemoryEvent(sender=sender, content=content, metadata=meta)
        if self.policy.should_write(event):
            self.store.add(event)

    def recall(self, query: str, k: int | None = None):
        raw = self.store.query(query, limit=max(k or self.retrieval_k, 10))
        return self.policy.select(raw, query, k or self.retrieval_k)

    # Aliases
    add_event = remember
    query     = recall
