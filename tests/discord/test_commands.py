from __future__ import annotations

from pathlib import Path

import pytest

from mnemos.app.errors import StorageError
from mnemos.discord.commands import _persist_active_model_change
from mnemos.inference.models import ModelManager
from mnemos.storage import InMemorySettingsStore, SQLiteSettingsStore


class _FailingSettingsStore:
    def get_active_model(self) -> str:
        return "kimi-k2.6"

    def set_active_model(self, model_id: str) -> None:
        raise StorageError("disk full")


def test_persist_active_model_change_updates_store_and_manager(tmp_path: Path) -> None:
    manager = ModelManager(active_model="kimi-k2.6")
    manager.set_available(["kimi-k2.6", "openai-gpt-5"])
    store = SQLiteSettingsStore(
        path=tmp_path / "state.db",
        default_active_model="kimi-k2.6",
    )

    active_model = _persist_active_model_change(manager, store, "openai-gpt-5")

    assert active_model == "openai-gpt-5"
    assert manager.current() == "openai-gpt-5"
    assert store.get_active_model() == "openai-gpt-5"


def test_persist_active_model_change_preserves_model_on_storage_error() -> None:
    manager = ModelManager(active_model="kimi-k2.6")
    manager.set_available(["kimi-k2.6", "openai-gpt-5"])

    with pytest.raises(StorageError, match="disk full"):
        _persist_active_model_change(manager, _FailingSettingsStore(), "openai-gpt-5")

    assert manager.current() == "kimi-k2.6"


def test_in_memory_settings_store_still_supports_simple_runtime_use() -> None:
    store = InMemorySettingsStore(active_model="kimi-k2.6")

    store.set_active_model("openai-gpt-5")

    assert store.get_active_model() == "openai-gpt-5"
