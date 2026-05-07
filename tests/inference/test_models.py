from __future__ import annotations

import pytest

from mnemos.inference.models import ModelManager


def test_model_manager_sets_known_model() -> None:
    manager = ModelManager(active_model="llama3.3-70b-instruct")
    manager.set_available(["llama3.3-70b-instruct", "anthropic-claude-4.6-sonnet"])

    manager.set_active("anthropic-claude-4.6-sonnet")

    assert manager.current() == "anthropic-claude-4.6-sonnet"


def test_model_manager_preserves_active_model_on_unknown_model() -> None:
    manager = ModelManager(active_model="llama3.3-70b-instruct")
    manager.set_available(["llama3.3-70b-instruct"])

    with pytest.raises(ValueError, match="unknown model"):
        manager.set_active("missing-model")

    assert manager.current() == "llama3.3-70b-instruct"
