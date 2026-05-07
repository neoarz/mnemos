from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass(slots=True)
class ModelManager:
    active_model: str
    available_models: frozenset[str] = field(default_factory=frozenset)

    def current(self) -> str:
        return self.active_model

    def set_available(self, model_ids: Iterable[str]) -> None:
        self.available_models = frozenset(
            model_id for model_id in model_ids if model_id
        )

    def set_active(self, model_id: str) -> None:
        self.active_model = self.validate(model_id)

    def list_available(self) -> list[str]:
        return sorted(self.available_models)

    def validate(self, model_id: str) -> str:
        cleaned = model_id.strip()
        if not cleaned:
            raise ValueError("model_id cannot be empty")
        if self.available_models and cleaned not in self.available_models:
            raise ValueError(f"unknown model: {cleaned}")
        return cleaned
