from __future__ import annotations

from mnemos.prompts import build_chat_messages


def test_build_chat_messages_includes_context_and_current_message() -> None:
    messages = build_chat_messages(
        author_name="Naz",
        user_message="what happened?",
        recent_context=["Alice: shipped the bot", "Bob: tested slash commands"],
    )

    assert messages[0].role == "system"
    assert messages[1].role == "user"
    assert "Alice: shipped the bot" in messages[1].content
    assert "Current message from Naz" in messages[1].content
    assert "what happened?" in messages[1].content


def test_build_chat_messages_only_advertises_tools_when_enabled() -> None:
    without_tools = build_chat_messages(
        author_name="Naz",
        user_message="read this url",
        recent_context=[],
    )
    with_tools = build_chat_messages(
        author_name="Naz",
        user_message="read this url",
        recent_context=[],
        tools_enabled=True,
    )

    assert "web_search" not in without_tools[0].content
    assert "read_url" not in without_tools[0].content
    assert "web_search" in with_tools[0].content
    assert "read_url" in with_tools[0].content
