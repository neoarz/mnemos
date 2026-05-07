from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from mnemos.app.errors import ConfigError
from mnemos.config.constants import (
    DEFAULT_CONTEXT_MESSAGES,
    DEFAULT_INFERENCE_URL,
    DEFAULT_MAX_COMPLETION_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_STATE_PATH,
    DEFAULT_TEMPERATURE,
    ENV_DIGITALOCEAN_DEFAULT_MODEL,
    ENV_DIGITALOCEAN_INFERENCE_URL,
    ENV_DIGITALOCEAN_MODEL_ACCESS_KEY,
    ENV_DISCORD_GUILD_ID,
    ENV_DISCORD_TOKEN,
    ENV_MAX_COMPLETION_TOKENS,
    ENV_MAX_CONTEXT_MESSAGES,
    ENV_MNEMOS_ADMIN_USER_IDS,
    ENV_MNEMOS_ALLOW_DISCORD_ADMINS,
    ENV_MNEMOS_STATE_PATH,
    ENV_TEMPERATURE,
)


@dataclass(frozen=True, slots=True)
class Settings:
    discord_token: str
    digitalocean_model_access_key: str
    discord_guild_id: int | None = None
    digitalocean_inference_url: str = DEFAULT_INFERENCE_URL
    digitalocean_default_model: str = DEFAULT_MODEL
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
        model_access_key = _required(values, ENV_DIGITALOCEAN_MODEL_ACCESS_KEY)

        return cls(
            discord_token=discord_token,
            digitalocean_model_access_key=model_access_key,
            discord_guild_id=_optional_int(values, ENV_DISCORD_GUILD_ID),
            digitalocean_inference_url=_optional_str(
                values,
                ENV_DIGITALOCEAN_INFERENCE_URL,
                DEFAULT_INFERENCE_URL,
            ).rstrip("/"),
            digitalocean_default_model=_optional_str(
                values,
                ENV_DIGITALOCEAN_DEFAULT_MODEL,
                DEFAULT_MODEL,
            ),
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
