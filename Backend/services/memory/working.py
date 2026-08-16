import threading
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import time

@dataclass
class MessageTurn:
    role: str
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkingMemory:
    """
    L1 Working Memory Context Window.
    Maintains a fast, thread-safe in-memory ring buffer of the active conversation turns.
    Prevents repeated vector database queries for recent conversation context.
    """
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self._history: List[MessageTurn] = []
        self._lock = threading.Lock()

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        with self._lock:
            turn = MessageTurn(role=role, content=content, metadata=metadata or {})
            self._history.append(turn)
            if len(self._history) > self.max_turns:
                self._history.pop(0)

    def get_history(self) -> List[Dict[str, str]]:
        with self._lock:
            return [{"role": m.role, "content": m.content} for m in self._history]

    def format_context_prompt(self) -> str:
        with self._lock:
            if not self._history:
                return ""
            formatted = []
            for m in self._history[-6:]:
                formatted.append(f"{m.role.capitalize()}: {m.content}")
            return "\n".join(formatted)

    def clear(self):
        with self._lock:
            self._history.clear()


# Global active working memory instance
working_memory = WorkingMemory(max_turns=10)
