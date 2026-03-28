"""
Admin commands — restricted to bot admins / server admins.
These commands help you manage the bot itself at runtime.
"""

import discord
from discord import app_commands, Interaction
from discord.ext import commands

import utils.embeds as em
from utils.checks import bot_admin_only
from utils.logger import setup_logger

logger = setup_logger("admin")


class Admin(commands.Cog):
    """Bot-administration commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── /reload ────────────────────────────────────────────────────────────────

    @app_commands.command(name="reload", description="Reload a bot extension (cog) at runtime.")
    @app_commands.describe(extension="Extension to reload, e.g. 'cogs.general'.")
    @bot_admin_only()
    async def reload(self, interaction: Interaction, extension: str) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.reload_extension(extension)
            logger.info(f"Extension '{extension}' reloaded by {interaction.user}.")
            await interaction.followup.send(
                embed=em.success("Extension Reloaded", f"`{extension}` was reloaded successfully.")
            )
        except commands.ExtensionNotLoaded:
            await interaction.followup.send(embed=em.error("Not Loaded", f"`{extension}` is not loaded."))
        except commands.ExtensionNotFound:
            await interaction.followup.send(embed=em.error("Not Found", f"`{extension}` does not exist."))
        except Exception as exc:
            logger.exception(f"Failed to reload '{extension}':")
            await interaction.followup.send(embed=em.error("Reload Failed", f"```{exc}```"))

    # ── /sync ──────────────────────────────────────────────────────────────────

    @app_commands.command(name="sync", description="Sync slash commands to Discord.")
    @app_commands.describe(guild_only="Sync to this guild only (faster) instead of globally.")
    @bot_admin_only()
    async def sync(self, interaction: Interaction, guild_only: bool = True) -> None:
        await interaction.response.defer(ephemeral=True)
        if guild_only:
            self.bot.tree.copy_global_to(guild=interaction.guild)
            synced = await self.bot.tree.sync(guild=interaction.guild)
        else:
            synced = await self.bot.tree.sync()
        scope = "this guild" if guild_only else "globally"
        logger.info(f"Synced {len(synced)} commands {scope} — requested by {interaction.user}.")
        await interaction.followup.send(
            embed=em.success("Commands Synced", f"Synced **{len(synced)}** command(s) {scope}.")
        )

    # ── /status ────────────────────────────────────────────────────────────────

    _activity_choices = [
        app_commands.Choice(name="Playing",   value="playing"),
        app_commands.Choice(name="Watching",  value="watching"),
        app_commands.Choice(name="Listening", value="listening"),
        app_commands.Choice(name="Competing", value="competing"),
    ]

    @app_commands.command(name="status", description="Change the bot's displayed activity status.")
    @app_commands.describe(activity_type="Type of activity.", text="Status text.")
    @app_commands.choices(activity_type=_activity_choices)
    @bot_admin_only()
    async def status(
        self,
        interaction: Interaction,
        activity_type: app_commands.Choice[str],
        text: str,
    ) -> None:
        type_map = {
            "playing":   discord.ActivityType.playing,
            "watching":  discord.ActivityType.watching,
            "listening": discord.ActivityType.listening,
            "competing": discord.ActivityType.competing,
        }
        activity = discord.Activity(type=type_map[activity_type.value], name=text)
        await self.bot.change_presence(activity=activity)
        await interaction.response.send_message(
            embed=em.success("Status Updated", f"Now **{activity_type.name}** *{text}*."),
            ephemeral=True,
        )

    # ── /listcogs ──────────────────────────────────────────────────────────────

    @app_commands.command(name="listcogs", description="List all loaded extensions (cogs).")
    @bot_admin_only()
    async def listcogs(self, interaction: Interaction) -> None:
        loaded = list(self.bot.extensions.keys())
        embed = em.info(
            title="📦  Loaded Extensions",
            description="\n".join(f"`{e}`" for e in loaded) or "None",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
