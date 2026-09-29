"""Shared discord.py helpers for the listener extensions."""

import sqlite3
from pathlib import Path

import discord


def database_path(guild_id: int) -> Path:
    return Path('Database') / f'{guild_id}.db'


def has_role(member: discord.Member, column: str) -> bool:
    with sqlite3.connect(database_path(member.guild.id)) as conn:
        owner, required = conn.execute(f'SELECT owner_role, {column} FROM config').fetchone()
    return member.id == member.guild.owner_id or any(role.id in (owner, required) for role in member.roles)


def view(*buttons: discord.ui.Button) -> discord.ui.View:
    result = discord.ui.View(timeout=None)
    for button in buttons:
        result.add_item(button)
    return result


async def setup(bot):
    """The package itself has no listeners to register."""
