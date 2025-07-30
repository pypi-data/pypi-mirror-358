"""A naive baseline policy"""

from typing import List

from ..core import MemoryEvent, MemoryPolicy


class BasicPolicy(MemoryPolicy):
    """Always write; keyword‑overlap retrieval"""

    def should_write(self, event: MemoryEvent) -> bool:
        return True

    def select(self, events: List[MemoryEvent], query: str, k: int):
        q_words = set(query.lower().split())
        ranked = []
        for ev in events:
            score = len(q_words & set(ev.content.lower().split()))
            ranked.append((score, ev))
        ranked.sort(key=lambda t: t[0], reverse=True)
        return [ev for _, ev in ranked[:k]]
