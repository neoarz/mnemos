from __future__ import annotations

import discord
from discord import app_commands
from mnemos.app.errors import StorageError
from mnemos.config import Settings
from mnemos.discord.constants import (
    EPHEMERAL_MESSAGE_LIMIT,
    MODEL_PERMISSION_DENIED_MESSAGE,
)
from mnemos.discord.text import split_discord_message
from mnemos.inference import ModelManager
from mnemos.storage import SettingsStore


def register_commands(
    tree: app_commands.CommandTree[discord.Client],
    *,
    settings: Settings,
    settings_store: SettingsStore,
    model_manager: ModelManager,
) -> None:
    model_group = app_commands.Group(
        name="model",
        description="Switch or inspect the active model",
    )

    @tree.command(name="status", description="Check if Mnemos is up")
    @app_commands.guild_only()
    async def status(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            f"Online — active model is `{model_manager.current()}`.",
            ephemeral=True,
        )

    @model_group.command(name="current", description="Show which model is active")
    @app_commands.guild_only()
    async def current_model(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            f"Currently using `{model_manager.current()}`.",
            ephemeral=True,
        )

    @model_group.command(name="list", description="List available models")
    @app_commands.guild_only()
    async def list_models(interaction: discord.Interaction) -> None:
        available = model_manager.list_available()
        content = "Available models:\n" + "\n".join(f"- `{m}`" for m in available)
        for chunk in split_discord_message(content, limit=EPHEMERAL_MESSAGE_LIMIT):
            await interaction.response.send_message(chunk, ephemeral=True)

    async def model_autocomplete(
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=m, value=m)
            for m in model_manager.list_available()
            if current.lower() in m.lower()
        ]

    @model_group.command(name="set", description="Switch to a different model")
    @app_commands.describe(model="Model to switch to")
    @app_commands.autocomplete(model=model_autocomplete)
    @app_commands.guild_only()
    async def set_model(interaction: discord.Interaction, model: str) -> None:
        if not _can_manage_models(interaction, settings):
            await interaction.response.send_message(
                MODEL_PERMISSION_DENIED_MESSAGE,
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        try:
            active_model = _persist_active_model_change(
                model_manager,
                settings_store,
                model,
            )
        except (StorageError, ValueError) as exc:
            await interaction.followup.send(
                f"Couldn't switch: {exc}",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            f"Switched to `{active_model}`.",
            ephemeral=True,
        )

    tree.add_command(model_group)


def _can_manage_models(interaction: discord.Interaction, settings: Settings) -> bool:
    if interaction.user.id in settings.mnemos_admin_user_ids:
        return True
    if not settings.mnemos_allow_discord_admins:
        return False
    return (
        isinstance(interaction.user, discord.Member)
        and interaction.user.guild_permissions.administrator
    )


def _persist_active_model_change(
    model_manager: ModelManager,
    settings_store: SettingsStore,
    model_id: str,
) -> str:
    cleaned = model_manager.validate(model_id)
    settings_store.set_active_model(cleaned)
    model_manager.set_active(cleaned)
    return cleaned
