from __future__ import annotations

from mnemos.discord.context import format_context
from mnemos.discord.types import ContextMessage


def test_format_context_compacts_message_whitespace() -> None:
    formatted = format_context(
        [
            ContextMessage(author_name="Alice", content="hello\n\nthere"),
            ContextMessage(author_name="Bob", content="   "),
        ]
    )

    assert formatted == ["Alice: hello there"]
