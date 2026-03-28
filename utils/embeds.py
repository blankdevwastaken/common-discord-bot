import discord
from datetime import datetime
from config import Config

def _base(color: int, title: str = "", description: str = "") -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow(),
    )
    return embed


def success(title: str = "Success", description: str = "") -> discord.Embed:
    embed = _base(Config.COLOR_SUCCESS, f"✅  {title}", description)
    return embed


def error(title: str = "Error", description: str = "") -> discord.Embed:
    embed = _base(Config.COLOR_ERROR, f"❌  {title}", description)
    return embed


def warning(title: str = "Warning", description: str = "") -> discord.Embed:
    embed = _base(Config.COLOR_WARNING, f"⚠️  {title}", description)
    return embed


def info(title: str = "Info", description: str = "") -> discord.Embed:
    embed = _base(Config.COLOR_INFO, f"ℹ️  {title}", description)
    return embed


def default(title: str = "", description: str = "") -> discord.Embed:
    embed = _base(Config.COLOR_DEFAULT, title, description)
    return embed


def with_author(
    embed: discord.Embed,
    user: discord.User | discord.Member,
) -> discord.Embed:
    """Attach a user's avatar and name as the embed author."""
    embed.set_author(name=str(user), icon_url=user.display_avatar.url)
    return embed


def paginate(
    items: list[str],
    title: str,
    per_page: int = 10,
    color: int = Config.COLOR_DEFAULT,
) -> list[discord.Embed]:
    """Split a list of strings into multiple embeds (pages)."""
    pages: list[discord.Embed] = []
    chunks = [items[i : i + per_page] for i in range(0, len(items), per_page)]
    for idx, chunk in enumerate(chunks, 1):
        embed = discord.Embed(
            title=title,
            description="\n".join(chunk),
            color=color,
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(text=f"Page {idx}/{len(chunks)}")
        pages.append(embed)
    return pages
