from __future__ import annotations

from mnemos.discord.constants import DISCORD_MESSAGE_LIMIT


def strip_bot_mentions(content: str, bot_user_id: int) -> str:
    return (
        content.replace(f"<@{bot_user_id}>", "")
        .replace(f"<@!{bot_user_id}>", "")
        .strip()
    )


def split_discord_message(
    content: str,
    limit: int = DISCORD_MESSAGE_LIMIT,
) -> list[str]:
    text = content.strip()
    if not text:
        return ["(No response)"]

    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        if remaining[limit] == " ":
            split_at = limit
        else:
            split_at = remaining.rfind("\n", 0, limit)
        if split_at < limit // 2:
            split_at = remaining.rfind(" ", 0, limit)
        if split_at < limit // 2:
            split_at = limit
        chunks.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()

    if remaining:
        chunks.append(remaining)
    return chunks
