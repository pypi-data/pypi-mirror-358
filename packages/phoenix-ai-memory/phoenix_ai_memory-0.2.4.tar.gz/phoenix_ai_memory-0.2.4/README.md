# Phoenix‑AI Memory

A **pluggable memory layer** for Agentic AI frameworks. It ships with adapters
for **in‑process**, **LangMem**, **Zep** and **Mem0** back‑ends, discovered
automatically via [Poetry entry points](https://python-poetry.org/docs/pyproject/).

```python
from phoenix_ai_memory import Memory

# picks backend from $PHOENIX_BACKEND (default: in_memory)
memory = Memory.from_env()

memory.remember("user", "I like classical music 🎵")
print(memory.recall("music")[0])
```