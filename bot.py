import discord
from discord.ext import commands
import asyncio
import logging
import os
import sys
from pathlib import Path

from config import Config
from utils.logger import setup_logger

# ─── Setup ───────────────────────────────────────────────────────────────────

logger = setup_logger("bot")

# ─── Bot Class ────────────────────────────────────────────────────────────────

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True

        super().__init__(
            command_prefix=Config.PREFIX,
            intents=intents,
            help_command=None,               # Custom one is in general.py
            case_insensitive=True,
        )

        self.config = Config
        self.initial_extensions: list[str] = [
            "cogs.general",
            "cogs.moderation",
            "cogs.admin",
            "cogs.error_handler",
        ]

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def setup_hook(self) -> None:
        """Called before the bot connects to Discord. Load cogs and sync tree."""
        logger.info("Loading extensions…")
        for ext in self.initial_extensions:
            try:
                await self.load_extension(ext)
                logger.info(f"  ✓ Loaded {ext}")
            except Exception as e:
                logger.error(f"  ✗ Failed to load {ext}: {e}", exc_info=True)

        # Sync slash commands globally (or to a test guild for faster updates)
        if Config.TEST_GUILD_ID:
            guild = discord.Object(id=Config.TEST_GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f"Slash commands synced to test guild {Config.TEST_GUILD_ID}")
        else:
            await self.tree.sync()
            logger.info("Slash commands synced globally")

    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(self.guilds)} servers | /help",
            )
        )

    async def on_guild_join(self, guild: discord.Guild) -> None:
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        logger.info(f"Removed from guild: {guild.name} (ID: {guild.id})")

# ─── Entry Point ──────────────────────────────────────────────────────────────

async def main() -> None:
    async with Bot() as bot:
        await bot.start(Config.TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shut down by user.")
