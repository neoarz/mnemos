from __future__ import annotations

import logging

import aiohttp

from mnemos.config import Settings
from mnemos.discord import MnemosDiscordClient
from mnemos.inference import DigitalOceanInferenceClient, ModelManager
from mnemos.inference.constants import AVAILABLE_MODELS
from mnemos.storage import SQLiteSettingsStore

log = logging.getLogger("mnemos")


async def run() -> None:
    settings = Settings.from_env()
    settings_store = SQLiteSettingsStore(
        path=settings.mnemos_state_path,
        default_active_model=settings.digitalocean_default_model,
    )
    model_manager = ModelManager(
        active_model=settings_store.get_active_model(),
        available_models=frozenset(AVAILABLE_MODELS),
    )
    async with aiohttp.ClientSession() as session:
        inference_client = DigitalOceanInferenceClient(
            base_url=settings.digitalocean_inference_url,
            model_access_key=settings.digitalocean_model_access_key,
            session=session,
        )
        client = MnemosDiscordClient(
            settings=settings,
            settings_store=settings_store,
            inference_client=inference_client,
            model_manager=model_manager,
        )
        log.info(
            "Starting Mnemos Discord bot with model=%s guild_id=%s",
            model_manager.current(),
            settings.discord_guild_id or "global",
        )
        await client.start(settings.discord_token)
