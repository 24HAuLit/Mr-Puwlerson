"""Database-backed checks for discord.py commands, components, and messages."""

from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from sqlite3 import connect

import discord
from discord.ext import commands

from mr_puwlerson.utils.message_config import ErrorMessage


def _guild(ctx: discord.Interaction | commands.Context | discord.Message) -> discord.Guild | None:
    return ctx.guild


def _user(ctx: discord.Interaction | commands.Context | discord.Message) -> discord.User | discord.Member:
    return ctx.user if isinstance(ctx, discord.Interaction) else ctx.author


def _database(guild: discord.Guild) -> Path:
    return Path("Database") / f"{guild.id}.db"


async def _error(ctx: discord.Interaction | commands.Context | discord.Message, text: str | None) -> None:
    if text is None:
        return
    if isinstance(ctx, discord.Interaction):
        if ctx.response.is_done():
            await ctx.followup.send(text, ephemeral=True)
        else:
            await ctx.response.send_message(text, ephemeral=True)
    elif isinstance(ctx, discord.Message):
        # Message replies cannot be ephemeral.
        await ctx.reply(text)
    elif isinstance(ctx, commands.Context):
        await ctx.send(text, ephemeral=True)


async def database_exists(ctx: discord.Interaction | commands.Context | discord.Message) -> bool:
    """Check for a guild database, notifying the caller when it is missing."""
    guild = _guild(ctx)
    if guild is None:
        return False
    if _database(guild).exists():
        return True
    await _error(ctx, ErrorMessage.database_not_found(guild.id))
    return False


async def _has_role(ctx: discord.Interaction | commands.Context | discord.Message, column: str) -> bool:
    guild = _guild(ctx)
    if guild is None:
        return False
    user = _user(ctx)
    with closing(connect(_database(guild))) as conn:
        role_id = conn.execute(f"SELECT {column} FROM config").fetchone()[0]
        owner_role = conn.execute("SELECT owner_role FROM config").fetchone()[0]
    return (user.id == guild.owner_id or any(
        role.id in (owner_role, role_id) for role in getattr(user, "roles", ())
    ))


async def is_staff(ctx: discord.Interaction | commands.Context | discord.Message) -> bool:
    """Check for the configured staff or owner role, or guild ownership."""
    return await _has_role(ctx, "staff_role")


async def is_admin(ctx: discord.Interaction | commands.Context | discord.Message) -> bool:
    """Check for the configured admin or owner role, or guild ownership."""
    return await _has_role(ctx, "admin_role")


async def is_owner(ctx: discord.Interaction | commands.Context | discord.Message) -> bool:
    """Check for the configured owner role or guild ownership."""
    return await _has_role(ctx, "owner_role")


async def ticket_parent(ctx: discord.Interaction | commands.Context | discord.Message) -> bool:
    """Require a channel under the configured ticket category."""
    guild = _guild(ctx)
    if guild is None:
        return False
    with closing(connect(_database(guild))) as conn:
        parent_id = conn.execute("SELECT ticket_parent FROM config").fetchone()[0]
    if getattr(ctx.channel, "parent_id", None) == parent_id:
        return True
    await _error(ctx, ErrorMessage.ChannelError(guild.id))
    return False


async def is_plugin(ctx: discord.Interaction | commands.Context | discord.Message, plugin: str) -> bool:
    """Require an enabled plugin."""
    guild = _guild(ctx)
    if guild is None:
        return False
    with closing(connect(_database(guild))) as conn:
        row = conn.execute("SELECT status FROM plugins WHERE name = ?", (plugin,)).fetchone()
    if row is not None and row[0] == "true":
        return True
    await _error(ctx, ErrorMessage.PluginError(guild.id, plugin))
    return False


async def is_blacklist(ctx: discord.Interaction | commands.Context | discord.Message, author_id: int) -> bool:
    """Return whether a user is blacklisted, notifying the caller if so."""
    guild = _guild(ctx)
    if guild is None:
        return False
    with closing(connect(_database(guild))) as conn:
        row = conn.execute("SELECT 1 FROM blacklist WHERE user_id = ?", (author_id,)).fetchone()
    if row is None:
        return False
    await _error(ctx, ErrorMessage.BlacklistError(guild.id))
    return True


async def is_cooldown(ctx: discord.Interaction | commands.Context | discord.Message) -> bool:
    """Return whether the caller has an active cooldown, notifying them if so."""
    guild = _guild(ctx)
    if guild is None:
        return False
    with closing(connect(_database(guild))) as conn:
        row = conn.execute("SELECT timestamp FROM cooldown WHERE user = ?", (_user(ctx).id,)).fetchone()
    now = int(datetime.now(UTC).timestamp())
    if row is None or row[0] < now:
        return False
    await _error(ctx, ErrorMessage.cooldown(guild.id, row[0] - now))
    return True
