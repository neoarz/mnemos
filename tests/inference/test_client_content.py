from __future__ import annotations

import pytest

from mnemos.app.errors import InferenceError
from mnemos.inference.client import _model_ids_from_response
from mnemos.inference.messages import coerce_content_to_text


def test_coerce_plain_string() -> None:
    assert coerce_content_to_text("  hi  ") == "hi"


def test_coerce_none() -> None:
    assert coerce_content_to_text(None) == ""


def test_coerce_text_parts_list() -> None:
    raw: object = [{"type": "text", "text": "a"}, {"type": "text", "text": "b"}]
    assert coerce_content_to_text(raw) == "ab"


def test_model_ids_from_response_reads_openai_compatible_payload() -> None:
    response = {"data": [{"id": "m-2"}, {"id": "m-1"}, {"id": "m-2"}]}
    assert _model_ids_from_response(response) == ["m-1", "m-2"]


def test_model_ids_from_response_requires_non_empty_result() -> None:
    with pytest.raises(InferenceError, match="No models returned"):
        _model_ids_from_response({"data": []})
