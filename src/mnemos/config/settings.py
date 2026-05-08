from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from mnemos.app.errors import ConfigError
from mnemos.config.constants import (
    DEFAULT_CONTEXT_MESSAGES,
    DEFAULT_MAX_COMPLETION_TOKENS,
    DEFAULT_STATE_PATH,
    DEFAULT_TEMPERATURE,
    ENV_DISCORD_GUILD_ID,
    ENV_DISCORD_TOKEN,
    ENV_EXA_API_KEY,
    ENV_MAX_COMPLETION_TOKENS,
    ENV_MAX_CONTEXT_MESSAGES,
    ENV_MNEMOS_ADMIN_USER_IDS,
    ENV_MNEMOS_ALLOW_DISCORD_ADMINS,
    ENV_MNEMOS_STATE_PATH,
    ENV_OPENAI_API_KEY,
    ENV_OPENAI_BASE_URL,
    ENV_OPENAI_DEFAULT_MODEL,
    ENV_TEMPERATURE,
)


@dataclass(frozen=True, slots=True)
class Settings:
    discord_token: str
    openai_api_key: str
    openai_base_url: str
    openai_default_model: str
    discord_guild_id: int | None = None
    exa_api_key: str | None = None
    mnemos_admin_user_ids: frozenset[int] = frozenset()
    mnemos_allow_discord_admins: bool = True
    mnemos_state_path: Path = Path(DEFAULT_STATE_PATH)
    max_context_messages: int = DEFAULT_CONTEXT_MESSAGES
    max_completion_tokens: int = DEFAULT_MAX_COMPLETION_TOKENS
    temperature: float = DEFAULT_TEMPERATURE

    @classmethod
    def from_env(
        cls,
        env: Mapping[str, str] | None = None,
        *,
        load_dotenv_file: bool = True,
    ) -> Settings:
        if load_dotenv_file:
            load_dotenv()

        values = os.environ if env is None else env
        discord_token = _required(values, ENV_DISCORD_TOKEN)
        openai_api_key = _required(values, ENV_OPENAI_API_KEY)
        openai_base_url = _required(values, ENV_OPENAI_BASE_URL)
        openai_default_model = _required(values, ENV_OPENAI_DEFAULT_MODEL)

        return cls(
            discord_token=discord_token,
            openai_api_key=openai_api_key,
            openai_base_url=openai_base_url.rstrip("/"),
            openai_default_model=openai_default_model,
            discord_guild_id=_optional_int(values, ENV_DISCORD_GUILD_ID),
            exa_api_key=values.get(ENV_EXA_API_KEY, "").strip() or None,
            mnemos_admin_user_ids=_int_set(values.get(ENV_MNEMOS_ADMIN_USER_IDS, "")),
            mnemos_allow_discord_admins=_optional_bool(
                values,
                ENV_MNEMOS_ALLOW_DISCORD_ADMINS,
                True,
            ),
            mnemos_state_path=Path(
                _optional_str(
                    values,
                    ENV_MNEMOS_STATE_PATH,
                    DEFAULT_STATE_PATH,
                )
            ),
            max_context_messages=_positive_int(
                values,
                ENV_MAX_CONTEXT_MESSAGES,
                DEFAULT_CONTEXT_MESSAGES,
            ),
            max_completion_tokens=_positive_int(
                values,
                ENV_MAX_COMPLETION_TOKENS,
                DEFAULT_MAX_COMPLETION_TOKENS,
            ),
            temperature=_temperature(values.get(ENV_TEMPERATURE)),
        )


def _required(env: Mapping[str, str], name: str) -> str:
    value = env.get(name, "").strip()
    if not value:
        raise ConfigError(f"{name} is required")
    return value


def _optional_str(env: Mapping[str, str], name: str, default: str) -> str:
    value = env.get(name, "").strip()
    return value or default


def _optional_int(env: Mapping[str, str], name: str) -> int | None:
    value = env.get(name, "").strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer") from exc


def _positive_int(env: Mapping[str, str], name: str, default: int) -> int:
    value = env.get(name, "").strip()
    if not value:
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer") from exc
    if parsed < 1:
        raise ConfigError(f"{name} must be greater than 0")
    return parsed


def _optional_bool(env: Mapping[str, str], name: str, default: bool) -> bool:
    value = env.get(name, "").strip().lower()
    if not value:
        return default
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ConfigError(f"{name} must be a boolean")


def _int_set(value: str) -> frozenset[int]:
    ids: set[int] = set()
    for item in value.split(","):
        stripped = item.strip()
        if not stripped:
            continue
        try:
            ids.add(int(stripped))
        except ValueError as exc:
            raise ConfigError(
                f"{ENV_MNEMOS_ADMIN_USER_IDS} must contain integers"
            ) from exc
    return frozenset(ids)


def _temperature(value: str | None) -> float:
    if value is None or not value.strip():
        return DEFAULT_TEMPERATURE
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ConfigError(f"{ENV_TEMPERATURE} must be a number") from exc
    if not 0 <= parsed <= 2:
        raise ConfigError(f"{ENV_TEMPERATURE} must be between 0 and 2")
    return parsed
