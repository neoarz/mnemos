from __future__ import annotations

import pytest

from mnemos.app.errors import ConfigError
from mnemos.config import Settings
from mnemos.config.constants import DEFAULT_CONTEXT_MESSAGES, DEFAULT_MODEL


def test_settings_load_required_values_and_defaults() -> None:
    settings = Settings.from_env(
        {
            "DISCORD_TOKEN": "discord-token",
            "DIGITALOCEAN_MODEL_ACCESS_KEY": "model-key",
            "MNEMOS_ADMIN_USER_IDS": "123, 456",
        },
        load_dotenv_file=False,
    )

    assert settings.discord_token == "discord-token"
    assert settings.digitalocean_model_access_key == "model-key"
    assert settings.digitalocean_default_model == DEFAULT_MODEL
    assert settings.mnemos_admin_user_ids == frozenset({123, 456})
    assert settings.max_context_messages == DEFAULT_CONTEXT_MESSAGES


def test_settings_requires_discord_token() -> None:
    with pytest.raises(ConfigError, match="DISCORD_TOKEN is required"):
        Settings.from_env(
            {"DIGITALOCEAN_MODEL_ACCESS_KEY": "model-key"},
            load_dotenv_file=False,
        )


def test_settings_rejects_invalid_admin_ids() -> None:
    with pytest.raises(ConfigError, match="MNEMOS_ADMIN_USER_IDS"):
        Settings.from_env(
            {
                "DISCORD_TOKEN": "discord-token",
                "DIGITALOCEAN_MODEL_ACCESS_KEY": "model-key",
                "MNEMOS_ADMIN_USER_IDS": "not-an-id",
            },
            load_dotenv_file=False,
        )
