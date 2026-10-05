import sqlite3
from datetime import UTC, datetime

import discord
from discord.ext import commands

from mr_puwlerson.listeners import database_path


class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log(self, guild, user, action, title, description, color):
        if not database_path(guild.id).exists():
            return
        with sqlite3.connect(database_path(guild.id)) as conn:
            row = conn.execute("SELECT id FROM logs_channels WHERE name = 'ban'").fetchone()
        if row is None:
            return
        async for entry in guild.audit_logs(limit=5, action=action):
            if entry.target.id == user.id:
                break
        else:
            return
        embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now(UTC))
        embed.add_field(name='__Staff :__', value=entry.user.mention)
        embed.add_field(name='__Membre :__', value=user.mention)
        if action == discord.AuditLogAction.ban:
            embed.add_field(name='__Raison :__', value=entry.reason or 'Aucune raison spécifié')
        embed.set_footer(text=f'Staff ID : {entry.user.id} | User ID : {user.id}')
        await self.bot.get_channel(row[0]).send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        await self.log(guild, user, discord.AuditLogAction.ban, '🛑・Nouveau bannissement', f'Un membre vient de se faire bannir de **{guild.name}**.', 0xFF2020)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        await self.log(guild, user, discord.AuditLogAction.unban, '🟢・Nouveau débannissement', f'Un membre vient de se faire débannir de **{guild.name}**.', 0x3FFF20)


async def setup(bot):
    await bot.add_cog(Ban(bot))
