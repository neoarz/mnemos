from __future__ import annotations

import asyncio
from typing import cast

import discord
import mnemos.discord.bot as bot
from mnemos.discord.bot import _show_typing_once


class TypingChannel:
    def __init__(self) -> None:
        self.calls = 0

    async def typing(self) -> None:
        self.calls += 1


class FailingTypingChannel:
    async def typing(self) -> None:
        raise discord.DiscordException("rate limited")


class SlowTypingChannel:
    async def typing(self) -> None:
        await asyncio.sleep(1)


def test_show_typing_once_uses_one_typing_request() -> None:
    channel = TypingChannel()

    asyncio.run(_show_typing_once(cast(discord.abc.Messageable, channel)))

    assert channel.calls == 1


def test_show_typing_once_ignores_discord_failures() -> None:
    asyncio.run(
        _show_typing_once(cast(discord.abc.Messageable, FailingTypingChannel()))
    )


def test_show_typing_once_times_out(monkeypatch) -> None:
    monkeypatch.setattr(bot, "TYPING_TIMEOUT_SECONDS", 0.01)

    asyncio.run(_show_typing_once(cast(discord.abc.Messageable, SlowTypingChannel())))
