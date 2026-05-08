from __future__ import annotations

import logging

import aiohttp
from exa_py import AsyncExa

from mnemos.config import Settings
from mnemos.discord import MnemosDiscordClient
from mnemos.inference import AgentRunner, InferenceClient, ModelManager
from mnemos.storage import SQLiteSettingsStore
from mnemos.tools import ToolExecutor

log = logging.getLogger("mnemos")


async def run() -> None:
    settings = Settings.from_env()
    settings_store = SQLiteSettingsStore(
        path=settings.mnemos_state_path,
        default_active_model=settings.openai_default_model,
    )
    active_model = settings_store.get_active_model()

    tool_executor: ToolExecutor | None = None
    if settings.exa_api_key:
        tool_executor = ToolExecutor(exa=AsyncExa(api_key=settings.exa_api_key))
        log.info("Exa tools enabled (web_search, read_url)")
    else:
        log.info("EXA_API_KEY not set - tools disabled")

    async with aiohttp.ClientSession() as session:
        inference_client = InferenceClient(
            base_url=settings.openai_base_url,
            api_key=settings.openai_api_key,
            session=session,
        )
        model_manager = ModelManager(active_model=active_model)
        model_manager.set_available(await inference_client.list_models())
        model_manager.set_active(active_model)
        agent_runner = AgentRunner(
            client=inference_client,
            tool_executor=tool_executor,
        )
        client = MnemosDiscordClient(
            settings=settings,
            settings_store=settings_store,
            agent_runner=agent_runner,
            model_manager=model_manager,
        )
        log.info(
            "Starting Mnemos Discord bot with model=%s guild_id=%s",
            model_manager.current(),
            settings.discord_guild_id or "global",
        )
        await client.start(settings.discord_token)
