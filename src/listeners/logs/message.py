import os.path
import sqlite3
import interactions
from datetime import datetime


class Message(interactions.Extension):

    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_listener(name="on_message_create")
    async def new_message(self, message: interactions.Message):
        channel = await message.get_channel()
        content = message.content
        if message.guild_id is None:
            return
        guild = await message.get_guild()

        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()
        logs_create = await interactions.get(self.bot, interactions.Channel, object_id=
        c.execute("SELECT id FROM logs_channels WHERE name = 'new'").fetchone()[0])
        is_hidden = c.execute(f"SELECT hidden FROM channels WHERE id = {channel.id}").fetchone()[0]

        conn.close()

        if message.author.bot:
            return
        else:
            if (is_hidden == 1) or (channel.type == interactions.ChannelType.DM):
                return
            else:
                em = interactions.Embed(
                    title="🖊️・Nouveau message",
                    url=message.url,
                    description=f"**{message.author.username}#{message.author.discriminator}** vient d'envoyer un message sur **{guild.name}** ({guild.id}) dans le salon **{channel.name}** ({channel.id})",
                    color=0x4CFF4C,
                    timestamp=datetime.utcnow()
                )
                if message.content != '':
                    em.add_field(name="**Message : **", value=content)
                if message.attachments is not None:
                    i: int = 0
                    for j in message.attachments:
                        em.add_field(name=f"**Attachment {i + 1} (type : {message.attachments[i].content_type}): **",
                                     value=message.attachments[i].url)
                        i += 1
                em.set_footer(text=f"Author ID : {message.author.id} | Message ID : {message.id}")

                await logs_create.send(embeds=em)

    @interactions.extension_listener(name="on_message_update")
    async def edit_message(self, before: interactions.Message, after: interactions.Message):
        old_content = before.content
        new_content = after.content
        channel = await after.get_channel()
        if after.guild_id is None:
            return
        guild = await after.get_guild()

        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()
        logs_edit = await interactions.get(self.bot, interactions.Channel, object_id=
        c.execute("SELECT id FROM logs_channels WHERE name='edit'").fetchone()[0])
        is_hidden = c.execute(f"SELECT hidden FROM channels WHERE id = {channel.id}").fetchone()[0]

        conn.close()

        if after.author.bot:
            return
        else:
            if (is_hidden == 1) or (channel.type == interactions.ChannelType.DM):
                return
            else:
                em2 = interactions.Embed(
                    title="📝・Modification de message",
                    url=after.url,
                    description=f"**{after.author.username}#{after.author.discriminator}** vient de modifier un message sur **{guild.name}** ({guild.id}) dans le salon **{channel.name}** ({channel.id})",
                    color=0xFFFF00,
                    timestamp=datetime.utcnow()
                )
                if after.content != '':
                    if old_content == '':
                        em2.add_field(name="**Ancien Message : **", value="Aucun message", inline=False)
                    else:
                        em2.add_field(name="**Ancien Message : **", value=old_content, inline=False)
                    em2.add_field(name="**Nouveau Message : **", value=new_content, inline=False)
                if before.attachments is not None:
                    i: int = 0
                    for j in before.attachments:
                        em2.add_field(
                            name=f"**Ancien Attachment {i + 1} (type : {before.attachments[i].content_type}): **",
                            value=before.attachments[i].url)
                        em2.add_field(
                            name=f"**Nouveau Attachment {i + 1} (type : {after.attachments[i].content_type}): **",
                            value=after.attachments[i].url)
                        i += 1
                em2.set_footer(text=f"Author ID : {after.author.id} | Message ID : {after.id}")

                await logs_edit.send(embeds=em2)

    @interactions.extension_listener(name="on_message_delete")
    async def message_delete(self, message: interactions.Message):
        user = message.author
        channel = await message.get_channel()
        content = message.content
        if message.guild_id is None:
            return
        guild = await message.get_guild()

        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        logs_delete = await interactions.get(self.bot, interactions.Channel, object_id=
        c.execute("SELECT id FROM logs_channels WHERE name='delete'").fetchone()[0])
        is_hidden = c.execute(f"SELECT hidden FROM channels WHERE id = {channel.id}").fetchone()[0]

        conn.close()

        if message.author is None:
            return
        elif message.author.bot:
            return
        else:
            if (is_hidden == 1) or (channel.type == interactions.ChannelType.DM):
                return
            else:
                em = interactions.Embed(
                    title="🗑️・Message supprimé",
                    description=f"Le message de **{user.username}#{user.discriminator}** dans le salon **{channel.name}** ({channel.id}) sur **{guild.name}** ({guild.id}) vient d'être supprimé.",
                    color=0xFF5A5A,
                    timestamp=datetime.utcnow()
                )
                if message.content != '':
                    em.add_field(name="**Message : **", value=content)
                if message.attachments is not None:
                    i: int = 0
                    for j in message.attachments:
                        em.add_field(name=f"**Attachment {i + 1} (type : {message.attachments[i].content_type}): **",
                                     value=message.attachments[i].url)
                        i += 1
                em.set_footer(text=f"User ID : {user.id} | Message ID : {message.id}")

                await logs_delete.send(embeds=em)


def setup(bot):
    Message(bot)
