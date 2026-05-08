from __future__ import annotations

import asyncio
from typing import Any, cast

from mnemos.inference.client import InferenceClient
from mnemos.inference.messages import ChatMessage
from mnemos.inference.runner import AgentRunner


class _FakeClient:
    def __init__(self, message: dict[str, object]) -> None:
        self.message = message

    async def complete_raw(self, **kwargs: Any) -> dict[str, object]:
        return {
            "choices": [
                {
                    "message": self.message,
                    "finish_reason": "stop",
                }
            ]
        }


def test_runner_accepts_multipart_assistant_content() -> None:
    client = _FakeClient(
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "hello "},
                {"type": "text", "text": "there"},
            ],
        }
    )
    runner = AgentRunner(
        client=cast(InferenceClient, client),
        tool_executor=None,
    )

    response = asyncio.run(
        runner.run(
            model="gpt-4o",
            messages=[ChatMessage(role="user", content="hi")],
            temperature=0.7,
            max_completion_tokens=100,
        )
    )

    assert response == "hello there"


def test_runner_uses_refusal_when_content_is_empty() -> None:
    client = _FakeClient(
        {
            "role": "assistant",
            "content": "",
            "refusal": "I cannot help with that",
        }
    )
    runner = AgentRunner(
        client=cast(InferenceClient, client),
        tool_executor=None,
    )

    response = asyncio.run(
        runner.run(
            model="gpt-4o",
            messages=[ChatMessage(role="user", content="hi")],
            temperature=0.7,
            max_completion_tokens=100,
        )
    )

    assert response == "I cannot help with that"
