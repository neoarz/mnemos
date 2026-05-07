from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ChatRole = Literal["system", "user", "assistant"]


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: ChatRole
    content: str

    def to_payload(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}
