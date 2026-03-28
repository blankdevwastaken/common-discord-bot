"""
Moderation commands — require appropriate Discord permissions.
"""

import discord
from discord import app_commands, Interaction
from discord.ext import commands
from datetime import timedelta

import utils.embeds as em
from utils.checks import moderator_only

# Simple in-memory warn store. Replace with a database for persistence.
_warns: dict[int, list[dict]] = {}   # {user_id: [{guild_id, reason, mod}]}


class Moderation(commands.Cog):
    """Commands for moderating members."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ── Helper ────────────────────────────────────────────────────────────────

    async def _dm_notify(
        self,
        user: discord.User | discord.Member,
        action: str,
        guild: discord.Guild,
        reason: str,
    ) -> None:
        """Try to DM a user about a moderation action. Silently ignore DM failures."""
        try:
            embed = em.warning(
                title=f"You have been {action} in {guild.name}",
                description=f"**Reason:** {reason}",
            )
            await user.send(embed=embed)
        except discord.HTTPException:
            pass

    # ── /kick ──────────────────────────────────────────────────────────────────

    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.describe(member="Member to kick.", reason="Reason for the kick.")
    @app_commands.default_permissions(kick_members=True)
    @app_commands.guild_only()
    async def kick(
        self,
        interaction: Interaction,
        member: discord.Member,
        reason: str = "No reason provided.",
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        if member.top_role >= interaction.user.top_role:
            return await interaction.followup.send(
                embed=em.error("You cannot kick someone with an equal or higher role."),
            )

        await self._dm_notify(member, "kicked", interaction.guild, reason)
        await member.kick(reason=f"{interaction.user}: {reason}")

        await interaction.followup.send(
            embed=em.success("Member Kicked", f"**{member}** has been kicked.\n**Reason:** {reason}")
        )

    # ── /ban ───────────────────────────────────────────────────────────────────

    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.describe(
        member="Member to ban.",
        reason="Reason for the ban.",
        delete_days="Days of messages to delete (0–7).",
    )
    @app_commands.default_permissions(ban_members=True)
    @app_commands.guild_only()
    async def ban(
        self,
        interaction: Interaction,
        member: discord.Member,
        reason: str = "No reason provided.",
        delete_days: app_commands.Range[int, 0, 7] = 0,
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        if member.top_role >= interaction.user.top_role:
            return await interaction.followup.send(
                embed=em.error("You cannot ban someone with an equal or higher role.")
            )

        await self._dm_notify(member, "banned", interaction.guild, reason)
        await member.ban(
            reason=f"{interaction.user}: {reason}",
            delete_message_days=delete_days,
        )
        await interaction.followup.send(
            embed=em.success("Member Banned", f"**{member}** has been banned.\n**Reason:** {reason}")
        )

    # ── /unban ─────────────────────────────────────────────────────────────────

    @app_commands.command(name="unban", description="Unban a user by their ID.")
    @app_commands.describe(user_id="The ID of the user to unban.", reason="Reason for the unban.")
    @app_commands.default_permissions(ban_members=True)
    @app_commands.guild_only()
    async def unban(
        self,
        interaction: Interaction,
        user_id: str,
        reason: str = "No reason provided.",
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            uid = int(user_id)
        except ValueError:
            return await interaction.followup.send(embed=em.error("Invalid user ID."))

        try:
            await interaction.guild.unban(discord.Object(id=uid), reason=reason)
            await interaction.followup.send(
                embed=em.success("User Unbanned", f"User `{uid}` has been unbanned.")
            )
        except discord.NotFound:
            await interaction.followup.send(embed=em.error("That user is not banned."))

    # ── /timeout ───────────────────────────────────────────────────────────────

    @app_commands.command(name="timeout", description="Timeout (mute) a member.")
    @app_commands.describe(
        member="Member to timeout.",
        minutes="Duration of the timeout in minutes.",
        reason="Reason for the timeout.",
    )
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.guild_only()
    async def timeout(
        self,
        interaction: Interaction,
        member: discord.Member,
        minutes: app_commands.Range[int, 1, 40320],   # max 28 days
        reason: str = "No reason provided.",
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        duration = timedelta(minutes=minutes)
        await member.timeout(duration, reason=f"{interaction.user}: {reason}")
        await self._dm_notify(
            member,
            f"timed out for {minutes} minute(s)",
            interaction.guild,
            reason,
        )
        await interaction.followup.send(
            embed=em.success(
                "Member Timed Out",
                f"**{member}** has been timed out for **{minutes}** minute(s).\n**Reason:** {reason}",
            )
        )

    # ── /purge ─────────────────────────────────────────────────────────────────

    @app_commands.command(name="purge", description="Bulk-delete messages in this channel.")
    @app_commands.describe(
        amount="Number of messages to delete (1–100).",
        member="Only delete messages from this member (optional).",
    )
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def purge(
        self,
        interaction: Interaction,
        amount: app_commands.Range[int, 1, 100],
        member: discord.Member | None = None,
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        if member:
            deleted = await interaction.channel.purge(limit=amount, check=lambda m: m.author == member)
        else:
            deleted = await interaction.channel.purge(limit=amount)

        desc = f"Deleted **{len(deleted)}** message(s)"
        if member:
            desc += f" from **{member}**"
        await interaction.followup.send(embed=em.success("Channel Purged", desc))

    # ── /warn ──────────────────────────────────────────────────────────────────

    @app_commands.command(name="warn", description="Warn a member.")
    @app_commands.describe(member="Member to warn.", reason="Reason for the warning.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def warn(
        self,
        interaction: Interaction,
        member: discord.Member,
        reason: str = "No reason provided.",
    ) -> None:
        uid = member.id
        _warns.setdefault(uid, []).append(
            {"guild_id": interaction.guild.id, "reason": reason, "mod": str(interaction.user)}
        )
        count = len([w for w in _warns[uid] if w["guild_id"] == interaction.guild.id])
        await self._dm_notify(member, "warned", interaction.guild, reason)
        await interaction.response.send_message(
            embed=em.warning(
                "Member Warned",
                f"**{member}** has been warned. (**{count}** warning(s) total)\n**Reason:** {reason}",
            ),
            ephemeral=True,
        )

    @app_commands.command(name="warnings", description="View warnings for a member.")
    @app_commands.describe(member="Member to look up.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def warnings(self, interaction: Interaction, member: discord.Member) -> None:
        guild_warns = [
            w for w in _warns.get(member.id, [])
            if w["guild_id"] == interaction.guild.id
        ]
        if not guild_warns:
            return await interaction.response.send_message(
                embed=em.info("No Warnings", f"**{member}** has no warnings."), ephemeral=True
            )

        embed = em.warning(title=f"⚠️  Warnings for {member}")
        for i, w in enumerate(guild_warns, 1):
            embed.add_field(
                name=f"Warning #{i}",
                value=f"**Reason:** {w['reason']}\n**By:** {w['mod']}",
                inline=False,
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))
