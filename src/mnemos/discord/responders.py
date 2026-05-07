from __future__ import annotations

import discord
from mnemos.discord.constants import DEFAULT_TRIGGER_CONTENT
from mnemos.discord.text import strip_bot_mentions
from mnemos.discord.types import Trigger, TriggerKind


async def detect_trigger(
    message: discord.Message,
    *,
    bot_user: discord.ClientUser,
) -> Trigger | None:
    if message.guild is None or message.author.bot:
        return None

    mentioned = any(user.id == bot_user.id for user in message.mentions)
    if mentioned:
        content = strip_bot_mentions(message.content, bot_user.id)
        content = content or DEFAULT_TRIGGER_CONTENT
        return Trigger(kind=TriggerKind.MENTION, content=content)

    if await _is_reply_to_bot(message, bot_user):
        content = message.clean_content.strip() or DEFAULT_TRIGGER_CONTENT
        return Trigger(kind=TriggerKind.REPLY, content=content)

    return None


async def _is_reply_to_bot(
    message: discord.Message,
    bot_user: discord.ClientUser,
) -> bool:
    reference = message.reference
    if reference is None or reference.message_id is None:
        return False

    resolved = reference.resolved
    if isinstance(resolved, discord.Message):
        return resolved.author.id == bot_user.id
    if resolved is not None:
        return False

    try:
        fetched = await message.channel.fetch_message(reference.message_id)
    except discord.DiscordException:
        return False
    return fetched.author.id == bot_user.id
