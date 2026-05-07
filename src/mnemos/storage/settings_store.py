from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from mnemos.app.errors import StorageError


class SettingsStore(Protocol):
    def get_active_model(self) -> str: ...

    def set_active_model(self, model_id: str) -> None: ...


@dataclass(slots=True)
class SQLiteSettingsStore:
    path: Path
    default_active_model: str

    def get_active_model(self) -> str:
        try:
            with closing(self._connect()) as conn:
                row = conn.execute(
                    "SELECT value FROM settings WHERE key = ?", ("active_model",)
                ).fetchone()
        except (sqlite3.Error, OSError) as exc:
            raise StorageError(f"Could not read settings from {self.path}") from exc
        if row and row[0].strip():
            return row[0].strip()
        return self.default_active_model

    def set_active_model(self, model_id: str) -> None:
        cleaned = model_id.strip()
        if not cleaned:
            raise StorageError("active model cannot be empty")
        try:
            with closing(self._connect()) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    ("active_model", cleaned),
                )
                conn.commit()
        except (sqlite3.Error, OSError) as exc:
            raise StorageError(
                f"Could not persist active model to {self.path}"
            ) from exc

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS settings "
            "(key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        conn.commit()
        return conn


@dataclass(slots=True)
class InMemorySettingsStore:
    active_model: str

    def get_active_model(self) -> str:
        return self.active_model

    def set_active_model(self, model_id: str) -> None:
        self.active_model = model_id
