from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TriggerKind(StrEnum):
    MENTION = "mention"
    REPLY = "reply"


@dataclass(frozen=True, slots=True)
class Trigger:
    kind: TriggerKind
    content: str


@dataclass(frozen=True, slots=True)
class ContextMessage:
    author_name: str
    content: str
