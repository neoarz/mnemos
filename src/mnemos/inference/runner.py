from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

from mnemos.app.errors import InferenceError
from mnemos.inference.client import InferenceClient
from mnemos.inference.constants import MAX_TOOL_ROUNDS
from mnemos.inference.messages import ChatMessage, coerce_content_to_text
from mnemos.tools.definitions import ALL_TOOLS
from mnemos.tools.executor import ToolExecutor


@dataclass(frozen=True, slots=True)
class AgentRunner:
    client: InferenceClient
    tool_executor: ToolExecutor | None

    @property
    def tools_enabled(self) -> bool:
        return self.tool_executor is not None

    async def run(
        self,
        *,
        model: str,
        messages: Sequence[ChatMessage],
        temperature: float,
        max_completion_tokens: int,
    ) -> str:
        history: list[dict[str, object]] = [
            cast(dict[str, object], m.to_payload()) for m in messages
        ]
        tools = ALL_TOOLS if self.tools_enabled else []

        for _ in range(MAX_TOOL_ROUNDS):
            raw = await self.client.complete_raw(
                model=model,
                messages=history,
                temperature=temperature,
                max_completion_tokens=max_completion_tokens,
                tools=tools or None,
            )

            choices = _as_list(raw.get("choices"), "choices")
            if not choices:
                raise InferenceError("No choices in response")
            choice = _as_dict(choices[0], "choice")
            message = _as_dict(choice.get("message"), "message")
            finish_reason = choice.get("finish_reason")

            tool_calls_raw = message.get("tool_calls")
            if finish_reason != "tool_calls" or not tool_calls_raw:
                return _extract_text(message)
            tool_executor = self.tool_executor
            if tool_executor is None:
                raise InferenceError("Tool calls returned but tools are disabled")

            history.append(dict(message))

            for tc_raw in _as_list(tool_calls_raw, "tool_calls"):
                tc = _as_dict(tc_raw, "tool_call")
                call_id = str(tc["id"])
                fn = _as_dict(tc.get("function"), "tool_call.function")
                name = str(fn["name"])
                arguments = str(fn["arguments"])
                result = await tool_executor.execute(name, arguments)
                history.append(
                    {
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": result,
                    }
                )

        raise InferenceError(
            f"Exceeded {MAX_TOOL_ROUNDS} tool-call rounds without a final response"
        )


def _extract_text(message: dict[str, object]) -> str:
    content = coerce_content_to_text(message.get("content"))
    if content:
        return content
    refusal = message.get("refusal")
    if isinstance(refusal, str) and refusal.strip():
        return refusal.strip()
    raise InferenceError("No text content in final response")


def _as_dict(value: object, label: str) -> dict[str, object]:
    if isinstance(value, dict):
        return cast(dict[str, object], value)
    raise InferenceError(f"Expected mapping for {label!r}, got {type(value).__name__}")


def _as_list(value: object, label: str) -> list[object]:
    if isinstance(value, list):
        return cast(list[object], value)
    raise InferenceError(f"Expected list for {label!r}, got {type(value).__name__}")
