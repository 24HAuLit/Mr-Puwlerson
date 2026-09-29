import sqlite3
from datetime import datetime, timezone

import discord
from discord.ext import commands

from mr_puwlerson.listeners import database_path


class JoinQuit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log(self, member, title, verb, color):
        guild = member.guild
        if not database_path(guild.id).exists():
            return
        with sqlite3.connect(database_path(guild.id)) as conn:
            row = conn.execute("SELECT id FROM logs_channels WHERE name = 'join-quit'").fetchone()
        if row is None:
            return
        embed = discord.Embed(title=title, description=f'**{member}** {verb} **{guild.name}**', color=color, timestamp=datetime.now(timezone.utc))
        embed.set_footer(text=f'Server ID : {guild.id} | User ID : {member.id}')
        await self.bot.get_channel(row[0]).send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.log(member, '🛬・Un utilisateur a rejoint un serveur', 'a rejoint', 0x4CFF4C)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.log(member, '🛫・Un utilisateur a quitté un serveur', 'a quitté', 0xFF5A5A)


async def setup(bot):
    await bot.add_cog(JoinQuit(bot))
