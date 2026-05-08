from __future__ import annotations

from collections.abc import Sequence

from mnemos.inference.messages import ChatMessage
from mnemos.prompts.system import build_system_prompt


def build_chat_messages(
    *,
    author_name: str,
    user_message: str,
    recent_context: Sequence[str],
    tools_enabled: bool = False,
) -> list[ChatMessage]:
    context = "\n".join(recent_context).strip() or "No recent channel context."
    content = (
        "Recent channel context:\n"
        f"{context}\n\n"
        f"Current message from {author_name}:\n"
        f"{user_message.strip()}"
    )
    return [
        ChatMessage(
            role="system",
            content=build_system_prompt(tools_enabled=tools_enabled),
        ),
        ChatMessage(role="user", content=content),
    ]
