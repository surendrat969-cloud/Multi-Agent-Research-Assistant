"""Conversation memory: buffer + summary persisted via chat repository."""
from __future__ import annotations

from typing import Optional

from database import ChatRepository
from models.schemas import ChatMessage


class ConversationMemory:
    """Per-session memory backed by SQLite and a rolling buffer."""

    def __init__(self, user_id: str, session_id: str, max_turns: int = 12) -> None:
        self.user_id = user_id
        self.session_id = session_id
        self.max_turns = max_turns
        self._buffer: list[ChatMessage] = []

    def load(self) -> "ConversationMemory":
        self._buffer = ChatRepository.history(self.user_id, self.session_id, limit=self.max_turns)
        return self

    def add_user(self, content: str) -> ChatMessage:
        msg = ChatRepository.add(self.user_id, self.session_id, "user", content)
        self._buffer.append(msg)
        self._trim()
        return msg

    def add_assistant(self, content: str) -> ChatMessage:
        msg = ChatRepository.add(self.user_id, self.session_id, "assistant", content)
        self._buffer.append(msg)
        self._trim()
        return msg

    def messages(self) -> list[ChatMessage]:
        return list(self._buffer)

    def as_prompt_context(self, max_chars: int = 2000) -> str:
        """Render recent turns into a compact string for the LLM."""
        if not self._buffer:
            return ""
        lines = []
        total = 0
        for m in reversed(self._buffer):
            line = f"{m.role.capitalize()}: {m.content}"
            if total + len(line) > max_chars:
                break
            lines.append(line)
            total += len(line)
        return "\n".join(reversed(lines))

    def clear(self) -> None:
        ChatRepository.delete_session(self.user_id, self.session_id)
        self._buffer = []

    def _trim(self) -> None:
        if len(self._buffer) > self.max_turns * 2:
            self._buffer = self._buffer[-(self.max_turns * 2) :]

    @property
    def last_assistant(self) -> Optional[str]:
        for m in reversed(self._buffer):
            if m.role == "assistant":
                return m.content
        return None
