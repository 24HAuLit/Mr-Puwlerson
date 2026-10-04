import sqlite3
from datetime import UTC, datetime

import discord
from discord.ext import commands

from mr_puwlerson.listeners import database_path


class Message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def log_channel(self, message, kind):
        if not message.guild or not database_path(message.guild.id).exists():
            return None
        with sqlite3.connect(database_path(message.guild.id)) as conn:
            parent = conn.execute('SELECT ticket_parent FROM config').fetchone()[0]
            if getattr(message.channel, 'category_id', None) == parent:
                return None
            hidden = conn.execute('SELECT hidden FROM channels WHERE id = ?', (message.channel.id,)).fetchone()
            if hidden is None or hidden[0] == 1:
                return None
            row = conn.execute('SELECT id FROM logs_channels WHERE name = ?', (kind,)).fetchone()
        return self.bot.get_channel(row[0]) if row else None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        logs = self.log_channel(message, 'new')
        if logs is None:
            return
        embed = discord.Embed(title='🖊️・Nouveau message', url=message.jump_url, description=f'**{message.author}** vient d\'envoyer un message sur **{message.guild.name}** ({message.guild.id}) dans le salon **{message.channel.name}** ({message.channel.id})', color=0x4CFF4C, timestamp=datetime.now(UTC))
        if message.content:
            embed.add_field(name='**Message : **', value=message.content[:1024])
        for i, attachment in enumerate(message.attachments):
            embed.add_field(name=f'**Attachment {i + 1} (type : {attachment.content_type}): **', value=attachment.url)
        embed.set_footer(text=f'Author ID : {message.author.id} | Message ID : {message.id}')
        await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, old: discord.Message, new: discord.Message):
        if new.author.bot or old.content == new.content and old.attachments == new.attachments:
            return
        logs = self.log_channel(new, 'edit')
        if logs is None:
            return
        embed = discord.Embed(title='📝・Modification de message', url=new.jump_url, description=f'**{new.author}** vient de modifier un message sur **{new.guild.name}** ({new.guild.id}) dans le salon **{new.channel.name}** ({new.channel.id})', color=0xFFFF00, timestamp=datetime.now(UTC))
        if new.content:
            embed.add_field(name='**Ancien Message : **', value=(old.content or 'Aucun message')[:1024], inline=False)
            embed.add_field(name='**Nouveau Message : **', value=new.content[:1024], inline=False)
        for i, attachment in enumerate(old.attachments):
            embed.add_field(name=f'**Ancien Attachment {i + 1} (type : {attachment.content_type}): **', value=attachment.url)
        for i, attachment in enumerate(new.attachments):
            embed.add_field(name=f'**Nouveau Attachment {i + 1} (type : {attachment.content_type}): **', value=attachment.url)
        embed.set_footer(text=f'Author ID : {new.author.id} | Message ID : {new.id}')
        await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.guild is None or not database_path(message.guild.id).exists():
            return
        with sqlite3.connect(database_path(message.guild.id)) as conn:
            conn.execute('DELETE FROM self_role WHERE message_id = ?', (message.id,))
        if message.author is None or message.author.bot:
            return
        logs = self.log_channel(message, 'delete')
        if logs is None:
            return
        embed = discord.Embed(title='🗑️・Message supprimé', description=f'Le message de **{message.author}** dans le salon **{message.channel.name}** ({message.channel.id}) sur **{message.guild.name}** ({message.guild.id}) vient d\'être supprimé.', color=0xFF5A5A, timestamp=datetime.now(UTC))
        if message.content:
            embed.add_field(name='**Message : **', value=message.content[:1024])
        for i, attachment in enumerate(message.attachments):
            embed.add_field(name=f'**Attachment {i + 1} (type : {attachment.content_type}): **', value=attachment.url)
        embed.set_footer(text=f'User ID : {message.author.id} | Message ID : {message.id}')
        await logs.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Message(bot))
