"""Memory façade and registry"""

from __future__ import annotations

import importlib
import os
from typing import Dict, Type

from .adapters.in_memory_store import InMemoryStore
from .core import MemoryEvent, MemoryPolicy, MemoryStore
from .policies.basic import BasicPolicy

# Attempt dynamic import of optional adapters
_DEFAULT_REGISTRY: Dict[str, Type[MemoryStore]] = {
    "in_memory": InMemoryStore,
}

for _name, _path in {
    "langmem": "phoenix_ai_memory.memory.adapters.langmem_store:LangMemStore",
    "zep": "phoenix_ai_memory.memory.adapters.zep_store:ZepStore",
    "mem0": "phoenix_ai_memory.memory.adapters.mem0_store:Mem0Store",
}.items():
    try:
        mod_name, attr = _path.split(":")
        _DEFAULT_REGISTRY[_name] = getattr(importlib.import_module(mod_name), attr)
    except Exception:
        # adapter import will raise if requirements missing; skip registration
        pass


class Memory:
    """High‑level user object"""

    def __init__(
        self,
        store: MemoryStore | None = None,
        policy: MemoryPolicy | None = None,
        retrieval_k: int = 5,
    ) -> None:
        self.store = store or InMemoryStore()
        self.policy = policy or BasicPolicy()
        self.retrieval_k = retrieval_k

    # ----- factory helpers -----
    @classmethod
    def from_env(cls) -> "Memory":
        backend = os.getenv("PHOENIX_BACKEND", "in_memory")
        retrieval_k = int(os.getenv("PHOENIX_RETRIEVAL_K", "5"))
        policy_name = os.getenv("PHOENIX_POLICY", "basic")
        # 🆕 optional JSON for constructor kwargs
        store_kwargs = json.loads(os.getenv("PHOENIX_STORE_KWARGS", "{}"))

        store_cls = _DEFAULT_REGISTRY.get(backend) ...
        store     = store_cls(**store_kwargs)          # ⬅️ forward kwargs
        if store_cls is None:
            # attempt fully‑qualified import string
            try:
                mod_name, attr = backend.split(":")
                store_cls = getattr(importlib.import_module(mod_name), attr)
            except Exception as exc:
                raise ValueError(f"Unknown backend '{backend}': {exc}") from exc

        store = store_cls()

        policy = BasicPolicy() if policy_name == "basic" else BasicPolicy()
        return cls(store=store, policy=policy, retrieval_k=retrieval_k)

    # ----- memory API -----
    def remember(self, sender: str, content: str, **metadata):
        event = MemoryEvent(sender=sender, content=content, metadata=metadata)
        if self.policy.should_write(event):
            self.store.add(event)

    def recall(self, query: str, k: int | None = None):
        raw = self.store.query(query, limit=max(k or self.retrieval_k, 10))
        return self.policy.select(raw, query, k or self.retrieval_k)

    # aliases
    add_event = remember
    query = recall
