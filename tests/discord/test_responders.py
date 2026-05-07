from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import cast

import discord
from mnemos.discord.responders import detect_trigger
from mnemos.discord.types import TriggerKind


def test_detect_trigger_ignores_dm() -> None:
    message = cast(
        discord.Message,
        SimpleNamespace(
            guild=None,
            author=SimpleNamespace(bot=False),
            mentions=[],
            reference=None,
        ),
    )
    bot_user = cast(discord.ClientUser, SimpleNamespace(id=123))

    assert asyncio.run(detect_trigger(message, bot_user=bot_user)) is None


def test_detect_trigger_accepts_mentions() -> None:
    message = cast(
        discord.Message,
        SimpleNamespace(
            guild=object(),
            author=SimpleNamespace(bot=False),
            mentions=[SimpleNamespace(id=123)],
            content="<@123> hello",
        ),
    )
    bot_user = cast(discord.ClientUser, SimpleNamespace(id=123))

    trigger = asyncio.run(detect_trigger(message, bot_user=bot_user))

    assert trigger is not None
    assert trigger.kind is TriggerKind.MENTION
    assert trigger.content == "hello"
