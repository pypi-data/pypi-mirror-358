"""Core abstractions for phoenix_ai_memory"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class MemoryEvent:
    """A single memory item"""

    sender: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:  # pragma: no cover
        return f"[{self.timestamp.isoformat()}] {self.sender}: {self.content}"


class MemoryStore(ABC):
    """Backend ‑ agnostic interface"""

    @abstractmethod
    def add(self, event: MemoryEvent) -> None:
        """Persist a memory event"""

    @abstractmethod
    def query(self, query: str, limit: int = 5) -> List[MemoryEvent]:
        """Retrieve events semantically relevant to *query*"""

    @abstractmethod
    def clear(self) -> None:
        """Remove all stored memories"""


class MemoryPolicy(ABC):
    """Policy controlling when to write & how to select"""

    @abstractmethod
    def should_write(self, event: MemoryEvent) -> bool: ...

    @abstractmethod
    def select(
        self, events: List[MemoryEvent], query: str, k: int
    ) -> List[MemoryEvent]: ...
