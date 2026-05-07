from __future__ import annotations

import logging
import time

import discord
from mnemos.app.errors import InferenceError
from mnemos.config import Settings
from mnemos.discord.commands import register_commands
from mnemos.discord.constants import CONTEXT_FAILURE_MESSAGE, INFERENCE_FAILURE_MESSAGE
from mnemos.discord.context import fetch_recent_context
from mnemos.discord.responders import detect_trigger
from mnemos.discord.text import split_discord_message
from mnemos.inference import DigitalOceanInferenceClient, ModelManager
from mnemos.prompts import build_chat_messages
from mnemos.storage import SettingsStore

log = logging.getLogger("mnemos.discord")


class MnemosDiscordClient(discord.Client):
    def __init__(
        self,
        *,
        settings: Settings,
        settings_store: SettingsStore,
        inference_client: DigitalOceanInferenceClient,
        model_manager: ModelManager,
    ) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.messages = True
        intents.message_content = True

        super().__init__(intents=intents)
        self.settings = settings
        self.settings_store = settings_store
        self.inference_client = inference_client
        self.model_manager = model_manager
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        register_commands(
            self.tree,
            settings=self.settings,
            settings_store=self.settings_store,
            model_manager=self.model_manager,
        )
        if self.settings.discord_guild_id is None:
            commands = await self.tree.sync()
            log.info("Synced %s global slash commands", len(commands))
            return

        guild = discord.Object(id=self.settings.discord_guild_id)
        self.tree.copy_global_to(guild=guild)
        commands = await self.tree.sync(guild=guild)
        log.info(
            "Synced %s slash commands for guild_id=%s",
            len(commands),
            self.settings.discord_guild_id,
        )

    async def on_ready(self) -> None:
        if self.user is None:
            log.info("Discord client is ready")
            return

        log.info(
            "Ready as %s (id=%s, guilds=%s, model=%s)",
            self.user,
            self.user.id,
            len(self.guilds),
            self.model_manager.current(),
        )

    async def on_message(self, message: discord.Message) -> None:
        if self.user is None:
            return

        started_at = time.perf_counter()
        trigger = await detect_trigger(message, bot_user=self.user)
        if trigger is None:
            return

        log.info("Responding to %s in %s", message.author, message.channel)
        async with message.channel.typing():
            try:
                context_started_at = time.perf_counter()
                recent_context = await fetch_recent_context(
                    message,
                    limit=self.settings.max_context_messages,
                )
                context_seconds = time.perf_counter() - context_started_at
                chat_messages = build_chat_messages(
                    author_name=message.author.display_name,
                    user_message=trigger.content,
                    recent_context=recent_context,
                )
                inference_started_at = time.perf_counter()
                response = await self.inference_client.complete(
                    model=self.model_manager.current(),
                    messages=chat_messages,
                    temperature=self.settings.temperature,
                    max_completion_tokens=self.settings.max_completion_tokens,
                )
                inference_seconds = time.perf_counter() - inference_started_at
                log.info(
                    "Generated response in %.2fs "
                    "(context=%.2fs, inference=%.2fs, context_messages=%s, "
                    "response_chars=%s)",
                    time.perf_counter() - started_at,
                    context_seconds,
                    inference_seconds,
                    len(recent_context),
                    len(response),
                )
            except InferenceError:
                log.exception("Inference failed")
                response = INFERENCE_FAILURE_MESSAGE
            except discord.DiscordException:
                log.exception("Discord context fetch failed")
                response = CONTEXT_FAILURE_MESSAGE

        send_started_at = time.perf_counter()
        try:
            await self._send_response(message, response)
        except discord.DiscordException:
            log.exception(
                "Failed to send response in %s (message=%s)",
                message.channel,
                message.id,
            )
            return
        log.info(
            "Sent response in %.2fs (total=%.2fs)",
            time.perf_counter() - send_started_at,
            time.perf_counter() - started_at,
        )

    async def _send_response(self, message: discord.Message, response: str) -> None:
        chunks = split_discord_message(response)
        first, *rest = chunks
        await message.reply(first, mention_author=False)
        for chunk in rest:
            await message.channel.send(chunk)
