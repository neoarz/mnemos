from __future__ import annotations

from mnemos.inference.client import _assistant_text, _coerce_content_to_text


def test_coerce_plain_string() -> None:
    assert _coerce_content_to_text("  hi  ") == "hi"


def test_coerce_none() -> None:
    assert _coerce_content_to_text(None) == ""


def test_coerce_text_parts_list() -> None:
    raw: object = [{"type": "text", "text": "a"}, {"type": "text", "text": "b"}]
    assert _coerce_content_to_text(raw) == "ab"


def test_assistant_text_prefers_content_over_refusal() -> None:
    message = {"content": "ok", "refusal": "no"}
    assert _assistant_text(message) == "ok"


def test_assistant_text_uses_refusal_when_content_empty() -> None:
    message = {"content": "", "refusal": "I cannot help with that"}
    assert _assistant_text(message) == "I cannot help with that"
