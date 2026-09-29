import sqlite3

import discord
from discord.ext import commands

from mr_puwlerson.listeners import database_path


class OnRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        guild = role.guild
        if not database_path(guild.id).exists():
            return
        with sqlite3.connect(database_path(guild.id)) as conn:
            conn.execute('INSERT INTO roles VALUES (?, ?, NULL)', (role.name, role.id))
            row = conn.execute("SELECT id FROM logs_channels WHERE name = 'create-role'").fetchone()
        if row:
            embed = discord.Embed(title='📝・Nouveau rôle', description=f'Un nouveau rôle vient d\'être créé sur **{guild.name}** ({guild.id})', color=0x4CFF4C)
            embed.add_field(name='**Nom : **', value=role.name)
            embed.add_field(name='**ID : **', value=str(role.id), inline=False)
            await self.bot.get_channel(row[0]).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        pass

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        pass


async def setup(bot):
    await bot.add_cog(OnRole(bot))
