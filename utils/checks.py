"""
Custom permission checks for slash commands.

Usage:
    from utils.checks import is_bot_admin, is_moderator

    @app_commands.check(is_bot_admin)
    async def my_command(interaction): ...
"""

import discord
from discord import app_commands, Interaction
from config import Config


# ─── Predicates ───────────────────────────────────────────────────────────────

def is_bot_admin(interaction: Interaction) -> bool:
    """
    True if the user is:
      • a server administrator, OR
      • has the configured BOT_ADMIN_ROLE_ID role.
    """
    if interaction.user.guild_permissions.administrator:
        return True
    if Config.BOT_ADMIN_ROLE_ID:
        role_ids = {r.id for r in interaction.user.roles}
        return Config.BOT_ADMIN_ROLE_ID in role_ids
    return False


def is_moderator(interaction: Interaction) -> bool:
    """
    True if the user has at least one of the common moderation permissions.
    Extend this list to suit your server's needs.
    """
    perms = interaction.user.guild_permissions
    return any([
        perms.administrator,
        perms.manage_messages,
        perms.kick_members,
        perms.ban_members,
        perms.manage_roles,
    ])


def is_guild_owner(interaction: Interaction) -> bool:
    """True if the user is the guild owner."""
    return interaction.user.id == interaction.guild.owner_id


# ─── Decorators (ready to use with @app_commands.check) ──────────────────────

def bot_admin_only():
    """Slash-command decorator: restrict to bot admins."""
    async def predicate(interaction: Interaction) -> bool:
        if not is_bot_admin(interaction):
            raise app_commands.CheckFailure(
                "You need the **Bot Admin** role or server-administrator "
                "permissions to use this command."
            )
        return True
    return app_commands.check(predicate)


def moderator_only():
    """Slash-command decorator: restrict to moderators."""
    async def predicate(interaction: Interaction) -> bool:
        if not is_moderator(interaction):
            raise app_commands.CheckFailure(
                "You need moderation permissions to use this command."
            )
        return True
    return app_commands.check(predicate)


def guild_owner_only():
    """Slash-command decorator: restrict to guild owner."""
    async def predicate(interaction: Interaction) -> bool:
        if not is_guild_owner(interaction):
            raise app_commands.CheckFailure(
                "Only the server owner can use this command."
            )
        return True
    return app_commands.check(predicate)
