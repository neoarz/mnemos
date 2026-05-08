from __future__ import annotations

from pathlib import Path

import pytest

from mnemos.app.errors import StorageError
from mnemos.storage import SQLiteSettingsStore


def test_sqlite_settings_store_uses_default_when_db_missing(tmp_path: Path) -> None:
    store = SQLiteSettingsStore(
        path=tmp_path / "state.db",
        default_active_model="gpt-4o",
    )

    assert store.get_active_model() == "gpt-4o"


def test_sqlite_settings_store_persists_and_retrieves_model(tmp_path: Path) -> None:
    store = SQLiteSettingsStore(
        path=tmp_path / "state.db",
        default_active_model="gpt-4o",
    )

    store.set_active_model("gpt-4o-mini")

    assert store.get_active_model() == "gpt-4o-mini"


def test_sqlite_settings_store_rejects_empty_model(tmp_path: Path) -> None:
    store = SQLiteSettingsStore(
        path=tmp_path / "state.db",
        default_active_model="gpt-4o",
    )

    with pytest.raises(StorageError, match="active model cannot be empty"):
        store.set_active_model("   ")
