from __future__ import annotations

from mnemos.discord.text import split_discord_message, strip_bot_mentions


def test_strip_bot_mentions_removes_standard_and_nickname_mentions() -> None:
    assert strip_bot_mentions("<@123> hello <@!123>", 123) == "hello"


def test_split_discord_message_keeps_chunks_under_limit() -> None:
    chunks = split_discord_message("alpha beta gamma", limit=10)

    assert chunks == ["alpha beta", "gamma"]
