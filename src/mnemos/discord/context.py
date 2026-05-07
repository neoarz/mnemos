from __future__ import annotations

from collections.abc import Iterable

import discord
from mnemos.discord.types import ContextMessage


async def fetch_recent_context(
    message: discord.Message,
    *,
    limit: int,
) -> list[str]:
    channel = message.channel
    if not hasattr(channel, "history"):
        return []

    collected: list[ContextMessage] = []
    async for item in channel.history(limit=limit, before=message):
        if item.author.bot or item.type is not discord.MessageType.default:
            continue
        content = item.clean_content.strip()
        if content:
            collected.append(
                ContextMessage(
                    author_name=item.author.display_name,
                    content=content,
                )
            )

    return format_context(reversed(collected))


def format_context(messages: Iterable[ContextMessage]) -> list[str]:
    formatted: list[str] = []
    for message in messages:
        content = " ".join(message.content.split())
        if content:
            formatted.append(f"{message.author_name}: {content}")
    return formatted
