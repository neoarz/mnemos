from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast

ChatRole = Literal["system", "user", "assistant"]


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: ChatRole
    content: str

    def to_payload(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


def coerce_content_to_text(raw: object) -> str:
    """Flatten OpenAI-compatible message content to a plain string."""
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, list):
        parts: list[str] = []
        for item in raw:
            if isinstance(item, str):
                parts.append(item)
                continue
            if not isinstance(item, dict):
                continue
            row = cast(dict[str, object], item)
            text = row.get("text")
            if isinstance(text, str):
                parts.append(text)
                continue
            nested = row.get("content")
            if isinstance(nested, str):
                parts.append(nested)
        return "".join(parts).strip()
    return ""
