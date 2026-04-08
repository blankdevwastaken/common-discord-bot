"""
General commands — available to everyone.
"""

import discord
import platform
import time
from discord import app_commands, Interaction
from discord.ext import commands

import utils.embeds as em

START_TIME = time.time()


class General(commands.Cog):
    """General-purpose commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── /ping ──────────────────────────────────────────────────────────────────

    @app_commands.command(name="ping", description="Check the bot's latency.")
    async def ping(self, interaction: Interaction) -> None:
        latency = round(self.bot.latency * 1000)
        embed = em.info(
            title="Pong! 🏓",
            description=f"**Websocket latency:** `{latency} ms`",
        )
        await interaction.response.send_message(embed=embed)

    # ── /help ──────────────────────────────────────────────────────────────────

    @app_commands.command(name="help", description="Show all available commands.")
    async def help(self, interaction: Interaction) -> None:
        embed = em.default(
            title="📖  Command Reference",
            description="Here's everything I can do. Use `/` to browse commands.",
        )

        embed.add_field(
            name="🌐  General",
            value=(
                "`/ping` — Latency check\n"
                "`/help` — This message\n"
                "`/info` — Bot information\n"
                "`/uptime` — How long I've been running\n"
                "`/avatar` — Show a user's avatar\n"
                "`/serverinfo` — Server details"
            ),
            inline=False,
        )
        embed.add_field(
            name="🔨  Moderation",
            value=(
                "`/kick` — Kick a member\n"
                "`/ban` — Ban a member\n"
                "`/unban` — Unban a user\n"
                "`/timeout` — Timeout a member\n"
                "`/purge` — Bulk-delete messages\n"
                "`/warn` — Warn a member"
            ),
            inline=False,
        )
        embed.add_field(
            name="⚙️  Admin",
            value=(
                "`/reload` — Reload an extension\n"
                "`/sync` — Re-sync slash commands\n"
                "`/status` — Change the bot's status"
            ),
            inline=False,
        )
        embed.add_field(
            name="📊  Level System",
            value=(
                "`/leaderboard` — View the active member leaderboard\n"
                "`/level` — Check your message count\n"
            ),
            inline=False,
        )
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ── /info ──────────────────────────────────────────────────────────────────

    @app_commands.command(name="info", description="Display information about the bot.")
    async def info(self, interaction: Interaction) -> None:
        embed = em.default(title="🤖  Bot Info")
        embed.add_field(name="Library",   value=f"discord.py {discord.__version__}", inline=True)
        embed.add_field(name="Python",    value=platform.python_version(), inline=True)
        embed.add_field(name="Platform",  value=platform.system(), inline=True)
        embed.add_field(name="Guilds",    value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Commands",  value=str(len(self.bot.tree.get_commands())), inline=True)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ── /uptime ────────────────────────────────────────────────────────────────

    @app_commands.command(name="uptime", description="Show how long the bot has been online.")
    async def uptime(self, interaction: Interaction) -> None:
        elapsed = int(time.time() - START_TIME)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        embed = em.info(
            title="⏱️  Uptime",
            description=f"`{hours}h {minutes}m {seconds}s`",
        )
        await interaction.response.send_message(embed=embed)

    # ── /avatar ────────────────────────────────────────────────────────────────

    @app_commands.command(name="avatar", description="Show a user's avatar.")
    @app_commands.describe(member="The member whose avatar to show (defaults to you).")
    async def avatar(
        self,
        interaction: Interaction,
        member: discord.Member | None = None,
    ) -> None:
        target = member or interaction.user
        embed = em.default(title=f"🖼️  {target.display_name}'s Avatar")
        embed.set_image(url=target.display_avatar.url)
        embed.add_field(
            name="Download",
            value=(
                f"[PNG]({target.display_avatar.with_format('png').url}) · "
                f"[JPG]({target.display_avatar.with_format('jpg').url}) · "
                f"[WEBP]({target.display_avatar.with_format('webp').url})"
            ),
        )
        await interaction.response.send_message(embed=embed)

    # ── /serverinfo ────────────────────────────────────────────────────────────

    @app_commands.command(name="serverinfo", description="Display information about this server.")
    @app_commands.guild_only()
    async def serverinfo(self, interaction: Interaction) -> None:
        guild = interaction.guild
        embed = em.default(title=f"🏰  {guild.name}")

        # Counts
        total   = guild.member_count
        bots    = sum(1 for m in guild.members if m.bot)
        humans  = total - bots
        online  = sum(1 for m in guild.members if m.status != discord.Status.offline)

        embed.add_field(name="Owner",        value=guild.owner.mention, inline=True)
        embed.add_field(name="Created",      value=discord.utils.format_dt(guild.created_at, "D"), inline=True)
        embed.add_field(name="Members",      value=f"{total} ({humans} humans / {bots} bots)", inline=False)
        embed.add_field(name="Online",       value=str(online), inline=True)
        embed.add_field(name="Channels",     value=f"{len(guild.text_channels)} text · {len(guild.voice_channels)} voice", inline=True)
        embed.add_field(name="Roles",        value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Boost Level",  value=f"Level {guild.premium_tier} ({guild.premium_subscription_count} boosts)", inline=True)
        embed.add_field(name="Verification", value=str(guild.verification_level).title(), inline=True)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner:
            embed.set_image(url=guild.banner.url)

        embed.set_footer(text=f"Guild ID: {guild.id}")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
