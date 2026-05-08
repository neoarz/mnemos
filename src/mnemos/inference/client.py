from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import cast

import aiohttp

from mnemos.app.errors import InferenceError
from mnemos.inference.constants import CHAT_COMPLETIONS_PATH, MODELS_PATH
from mnemos.inference.messages import ChatMessage


@dataclass(frozen=True, slots=True)
class InferenceClient:
    base_url: str
    api_key: str
    session: aiohttp.ClientSession
    timeout_seconds: float = 60

    async def complete(
        self,
        *,
        model: str,
        messages: Sequence[ChatMessage],
        temperature: float,
        max_completion_tokens: int,
    ) -> str:
        payload: dict[str, object] = {
            "model": model,
            "messages": [message.to_payload() for message in messages],
            "temperature": temperature,
            "max_completion_tokens": max_completion_tokens,
        }
        data = await self._request_json("POST", CHAT_COMPLETIONS_PATH, payload)
        root = _as_mapping(data, "chat completion response")
        choices = _as_sequence(root.get("choices"), "choices")
        if not choices:
            raise InferenceError("Inference returned no choices")

        choice = _as_mapping(choices[0], "choice")
        message = _as_mapping(choice.get("message"), "message")
        text = _assistant_text(message)
        if text:
            return text
        finish = choice.get("finish_reason")
        refusal = message.get("refusal")
        tool_calls = message.get("tool_calls")
        raise InferenceError(
            "No assistant text in response "
            f"(finish_reason={finish!r}, "
            f"refusal={refusal!r}, tool_calls present={tool_calls is not None})"
        )

    async def list_models(self) -> list[str]:
        data = await self._request_json("GET", MODELS_PATH)
        return _model_ids_from_response(data)

    async def _request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None = None,
    ) -> object:
        url = f"{self.base_url.rstrip('/')}{path}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)

        try:
            async with self.session.request(
                method,
                url,
                headers=headers,
                json=payload,
                timeout=timeout,
            ) as response:
                if response.status < 200 or response.status >= 300:
                    body = await response.text()
                    raise InferenceError(
                        f"Inference request failed with HTTP {response.status}: {body[:300]}"
                    )
                return await response.json()
        except TimeoutError as exc:
            raise InferenceError("Inference request timed out") from exc
        except aiohttp.ClientError as exc:
            message = f"Inference request failed: {exc}"
            raise InferenceError(message) from exc


def _assistant_text(message: Mapping[str, object]) -> str:
    text = _coerce_content_to_text(message.get("content"))
    if text:
        return text
    refusal = message.get("refusal")
    if isinstance(refusal, str) and refusal.strip():
        return refusal.strip()
    return ""


def _model_ids_from_response(data: object) -> list[str]:
    root = _as_mapping(data, "models response")
    rows = _as_sequence(root.get("data"), "models data")
    model_ids: list[str] = []
    for row in rows:
        model = _as_mapping(row, "model")
        model_id = model.get("id")
        if not isinstance(model_id, str) or not model_id.strip():
            raise InferenceError("Invalid model id")
        model_ids.append(model_id.strip())
    if not model_ids:
        raise InferenceError("No models returned")
    return sorted(set(model_ids))


def _coerce_content_to_text(raw: object) -> str:
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, list):
        parts: list[str] = []
        for item in raw:
            if isinstance(item, str):
                parts.append(item)
                continue
            if not isinstance(item, dict):
                continue
            row = cast(dict[str, object], item)
            text = row.get("text")
            if isinstance(text, str):
                parts.append(text)
                continue
            nested = row.get("content")
            if isinstance(nested, str):
                parts.append(nested)
        return "".join(parts).strip()
    return ""


def _as_mapping(value: object, label: str) -> dict[str, object]:
    if isinstance(value, dict) and all(isinstance(key, str) for key in value):
        return cast(dict[str, object], value)
    raise InferenceError(f"Invalid {label}")


def _as_sequence(value: object, label: str) -> list[object]:
    if isinstance(value, list):
        return cast(list[object], value)
    raise InferenceError(f"Invalid {label}")
