from __future__ import annotations

from pathlib import Path

import pytest

from mnemos.app.errors import StorageError
from mnemos.discord.commands import _persist_active_model_change
from mnemos.inference.models import ModelManager
from mnemos.storage import InMemorySettingsStore, SQLiteSettingsStore


class _FailingSettingsStore:
    def get_active_model(self) -> str:
        return "gpt-4o"

    def set_active_model(self, model_id: str) -> None:
        raise StorageError("disk full")


def test_persist_active_model_change_updates_store_and_manager(tmp_path: Path) -> None:
    manager = ModelManager(active_model="gpt-4o")
    manager.set_available(["gpt-4o", "gpt-4o-mini"])
    store = SQLiteSettingsStore(
        path=tmp_path / "state.db",
        default_active_model="gpt-4o",
    )

    active_model = _persist_active_model_change(manager, store, "gpt-4o-mini")

    assert active_model == "gpt-4o-mini"
    assert manager.current() == "gpt-4o-mini"
    assert store.get_active_model() == "gpt-4o-mini"


def test_persist_active_model_change_preserves_model_on_storage_error() -> None:
    manager = ModelManager(active_model="gpt-4o")
    manager.set_available(["gpt-4o", "gpt-4o-mini"])

    with pytest.raises(StorageError, match="disk full"):
        _persist_active_model_change(manager, _FailingSettingsStore(), "gpt-4o-mini")

    assert manager.current() == "gpt-4o"


def test_in_memory_settings_store_still_supports_simple_runtime_use() -> None:
    store = InMemorySettingsStore(active_model="gpt-4o")

    store.set_active_model("gpt-4o-mini")

    assert store.get_active_model() == "gpt-4o-mini"
