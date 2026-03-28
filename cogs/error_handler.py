"""
Global error handler.
Catches all unhandled app_command errors and sends a clean embed to the user.
"""

import discord
from discord import app_commands, Interaction
from discord.ext import commands

import utils.embeds as em
from utils.logger import setup_logger

logger = setup_logger("error_handler")


class ErrorHandler(commands.Cog):
    """Handles all unhandled application-command errors."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        # Attach the handler to the command tree
        bot.tree.on_error = self.on_app_command_error

    async def on_app_command_error(
        self,
        interaction: Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        """
        Called whenever a slash command raises an unhandled exception.
        We respond with a user-friendly embed and log the real error.
        """
        # Unwrap the error if it's wrapped in CommandInvokeError
        original = getattr(error, "original", error)

        # ── User-facing errors (expected) ─────────────────────────────────────

        if isinstance(original, app_commands.CheckFailure):
            embed = em.error("Permission Denied", str(original) or "You don't have permission to use this command.")

        elif isinstance(original, app_commands.CommandOnCooldown):
            retry = round(original.retry_after, 1)
            embed = em.warning("Slow Down!", f"This command is on cooldown. Try again in **{retry}s**.")

        elif isinstance(original, app_commands.MissingPermissions):
            missing = ", ".join(f"`{p}`" for p in original.missing_permissions)
            embed = em.error("Missing Permissions", f"You need: {missing}")

        elif isinstance(original, app_commands.BotMissingPermissions):
            missing = ", ".join(f"`{p}`" for p in original.missing_permissions)
            embed = em.error("I'm Missing Permissions", f"I need: {missing}")

        elif isinstance(original, discord.Forbidden):
            embed = em.error("Forbidden", "I don't have permission to do that.")

        elif isinstance(original, discord.NotFound):
            embed = em.error("Not Found", "That resource could not be found.")

        elif isinstance(original, app_commands.CommandNotFound):
            embed = em.error("Unknown Command", "That command doesn't exist.")

        elif isinstance(original, app_commands.TransformerError):
            embed = em.error("Invalid Input", str(original))

        # ── Unexpected errors (log fully) ─────────────────────────────────────
        else:
            command_name = interaction.command.name if interaction.command else "unknown"
            logger.exception(
                f"Unhandled error in /{command_name} "
                f"(user={interaction.user}, guild={interaction.guild_id}): {original}"
            )
            embed = em.error(
                "Something Went Wrong",
                "An unexpected error occurred. The developers have been notified.",
            )

        # ── Send the embed ────────────────────────────────────────────────────
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.HTTPException:
            pass  # If we can't even send the error, silently give up


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ErrorHandler(bot))
