import sqlite3

import discord
from discord.ext import commands

from mr_puwlerson.listeners import database_path


class OnChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log(self, channel, event):
        guild = channel.guild
        if not database_path(guild.id).exists():
            return
        with sqlite3.connect(database_path(guild.id)) as conn:
            if getattr(channel, 'category_id', None) == conn.execute('SELECT ticket_parent FROM config').fetchone()[0]:
                return
            if event == 'create':
                conn.execute('INSERT INTO channels VALUES (?, ?, NULL, 0)', (channel.name, channel.id))
            else:
                conn.execute('DELETE FROM channels WHERE id = ?', (channel.id,))
            name = 'create-channel' if event == 'create' else 'delete-channel'
            row = conn.execute('SELECT id FROM logs_channels WHERE name = ?', (name,)).fetchone()
        if row is None:
            return
        types = {discord.ChannelType.text: 'Text', discord.ChannelType.voice: 'Voice', discord.ChannelType.category: 'Category', discord.ChannelType.news: 'Announcement', discord.ChannelType.stage_voice: 'Stage Voice', discord.ChannelType.forum: 'Forum'}
        embed = discord.Embed(title='📝・Nouveau salon' if event == 'create' else '🗑️・Suppression de salon', description=f'Un salon vient d\'être {"créé" if event == "create" else "supprimé"} sur **{guild.name}** ({guild.id})', color=0x4CFF4C if event == 'create' else 0xFF5A5A)
        embed.add_field(name='**Nom : **', value=channel.name)
        embed.add_field(name='**Type : **', value=types.get(channel.type, channel.type.name))
        embed.add_field(name='**ID : **', value=str(channel.id), inline=False)
        await self.bot.get_channel(row[0]).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        await self.log(channel, 'create')

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        await self.log(channel, 'delete')


async def setup(bot):
    await bot.add_cog(OnChannel(bot))
