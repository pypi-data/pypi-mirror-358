"""Adapter for Zep memory service"""

from __future__ import annotations

from typing import List

from ..core import MemoryEvent, MemoryStore


class ZepStore(MemoryStore):
    def __init__(
        self, api_key: str | None = None, url: str | None = None, **kwargs
    ) -> None:
        try:
            from zep_python import ZepClient  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "zep-python is not installed. Run `pip install zep-python` or add the `zep` extra."
            ) from exc

        self._client = ZepClient(
            base_url=url or "https://api.getzep.com",
            api_key=api_key,
            **kwargs,
        )
        # Create a default session for demo purposes
        import uuid

        self._session_id = kwargs.get("session_id") or uuid.uuid4().hex

    def add(self, event: MemoryEvent) -> None:
        self._client.memory.add(
            session_id=self._session_id,
            role=event.sender,
            content=event.content,
            metadata=event.metadata,
        )

    def query(self, query: str, limit: int = 5) -> List[MemoryEvent]:
        search_results = self._client.memory.search(
            session_id=self._session_id,
            query=query,
            limit=limit,
        )
        results: List[MemoryEvent] = []
        for r in search_results:
            results.append(
                MemoryEvent(
                    sender=r.get("role", "assistant"),
                    content=r["content"],
                    metadata=r.get("metadata", {}),
                    timestamp=r.get("created_at"),
                )
            )
        return results

    def clear(self) -> None:
        self._client.memory.delete_session(self._session_id)
