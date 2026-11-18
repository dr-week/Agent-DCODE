"""
Short-term Working Memory with sliding-window message buffer and scratchpad key-value store.
"""

from typing import Any, Dict, List


class WorkingMemory:
    """Manages active turn history and scratchpad variables within a token/message budget."""

    def __init__(self, max_messages: int = 12):
        self.max_messages = max_messages
        self.messages: List[Dict[str, str]] = []
        self.scratchpad: Dict[str, Any] = {}

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def set_var(self, key: str, value: Any) -> None:
        self.scratchpad[key] = value

    def get_var(self, key: str, default: Any = None) -> Any:
        return self.scratchpad.get(key, default)

    def format_prompt_history(self) -> str:
        return "\n".join(f"[{m['role'].upper()}]: {m['content']}" for m in self.messages)

    def clear(self) -> None:
        self.messages.clear()
        self.scratchpad.clear()
