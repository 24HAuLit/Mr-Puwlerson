import sqlite3
import interactions
from interactions.api.events import MessageCreate, MessageUpdate, MessageDelete
from interactions.client.utils import get_all
from src.utils.checks import database_exists


class Message(interactions.Extension):

    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.listen(MessageCreate)
    async def new_message(self, new_message: MessageCreate):
        message = new_message.message
        channel = message.channel
        content = message.content
        guild = message.guild

        if message.author.bot:
            return

        if guild is None:
            return

        if await database_exists(new_message) is not True:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        ticket_parent = get_all(guild.channels, parent_id=c.execute("SELECT id FROM channels WHERE type = 'ticket_parent'").fetchone()[0])

        if channel in ticket_parent:
            return conn.close()

        logs_create = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'new'").fetchone()[0])
        is_hidden = c.execute(f"SELECT hidden FROM channels WHERE id = {channel.id}").fetchone()[0]

        conn.close()

        if (is_hidden == 1) or (channel.type == interactions.ChannelType.DM):
            return
        else:
            if message.author.discriminator == "0":
                em = interactions.Embed(
                    title="🖊️・Nouveau message",
                    url=message.jump_url,
                    description=f"**{message.author.username}** vient d'envoyer un message sur **{guild.name}** ({guild.id}) dans le salon **{channel.name}** ({channel.id})",
                    color=0x4CFF4C,
                    timestamp=interactions.Timestamp.utcnow()
                )
            else:
                em = interactions.Embed(
                    title="🖊️・Nouveau message",
                    url=message.jump_url,
                    description=f"**{message.author.username}#{message.author.discriminator}** vient d'envoyer un message sur **{guild.name}** ({guild.id}) dans le salon **{channel.name}** ({channel.id})",
                    color=0x4CFF4C,
                    timestamp=interactions.Timestamp.utcnow()
                )
            if message.content != '':
                em.add_field(name="**Message : **", value=content)
            if message.attachments is not None:
                i: int = 0
                for _ in message.attachments:
                    em.add_field(name=f"**Attachment {i + 1} (type : {message.attachments[i].content_type}): **",
                                 value=message.attachments[i].url)
                    i += 1
            em.set_footer(text=f"Author ID : {message.author.id} | Message ID : {message.id}")

            return await logs_create.send(embeds=em)

    @interactions.listen(MessageUpdate)
    async def edit_message(self, message: MessageUpdate):
        old = message.before
        new = message.after

        if old is None:
            return

        old_content = old.content
        new_content = new.content
        channel = new.channel
        guild = new.guild

        if guild is None:
            return

        if new.author.bot:
            return

        if await database_exists(new) is not True:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        ticket_parent = get_all(guild.channels, parent_id=c.execute("SELECT id FROM channels WHERE type = 'ticket_parent'").fetchone()[0])

        if channel in ticket_parent:
            return conn.close()

        logs_edit = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name='edit'").fetchone()[0])
        is_hidden = c.execute(f"SELECT hidden FROM channels WHERE id = {channel.id}").fetchone()[0]

        conn.close()

        if (is_hidden == 1) or (channel.type == interactions.ChannelType.DM):
            return
        else:
            if new.author.discriminator == "0":
                em2 = interactions.Embed(
                    title="📝・Modification de message",
                    url=new.jump_url,
                    description=f"**{new.author.username}** vient de modifier un message sur **{guild.name}** ({guild.id}) dans le salon **{channel.name}** ({channel.id})",
                    color=0xFFFF00,
                    timestamp=interactions.Timestamp.utcnow()
                )
            else:
                em2 = interactions.Embed(
                    title="📝・Modification de message",
                    url=new.jump_url,
                    description=f"**{new.author.username}#{new.author.discriminator}** vient de modifier un message sur **{guild.name}** ({guild.id}) dans le salon **{channel.name}** ({channel.id})",
                    color=0xFFFF00,
                    timestamp=interactions.Timestamp.utcnow()
                )
            if new.content != '':
                if old_content == '':
                    em2.add_field(name="**Ancien Message : **", value="Aucun message", inline=False)
                else:
                    em2.add_field(name="**Ancien Message : **", value=old_content, inline=False)
                em2.add_field(name="**Nouveau Message : **", value=new_content, inline=False)
            if old.attachments is not None:
                i: int = 0
                for _ in old.attachments:
                    em2.add_field(
                        name=f"**Ancien Attachment {i + 1} (type : {old.attachments[i].content_type}): **",
                        value=old.attachments[i].url)
                    em2.add_field(
                        name=f"**Nouveau Attachment {i + 1} (type : {new.attachments[i].content_type}): **",
                        value=new.attachments[i].url)
                    i += 1
            em2.set_footer(text=f"Author ID : {new.author.id} | Message ID : {new.id}")

            return await logs_edit.send(embeds=em2)

    @interactions.listen(MessageDelete)
    async def message_delete(self, del_message: MessageDelete):
        message = del_message.message
        user = message.author
        channel = message.channel
        guild = message.guild

        if guild is None:
            return

        if await database_exists(del_message) is not True:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if type(del_message.message) == interactions.models.discord.message.BaseMessage:
            history = guild.audit_log_history(action_type=72, limit=1)
            audit = await history.flatten()
            c.execute(f"DELETE FROM self_role WHERE message_id = {audit[0].id}")
            conn.commit()
            return conn.close()
        else:
            content = message.content

        if message.author.bot:
            return

        ticket_parent = get_all(guild.channels, parent_id=c.execute("SELECT id FROM channels WHERE type = 'ticket_parent'").fetchone()[0])

        if channel in ticket_parent:
            return conn.close()

        logs_delete = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name='delete'").fetchone()[0])
        is_hidden = c.execute(f"SELECT hidden FROM channels WHERE id = {channel.id}").fetchone()[0]

        c.execute(f"DELETE FROM self_role WHERE message_id = {message.id}")
        conn.commit()

        conn.close()

        if message.author is None:
            return
        else:
            if (is_hidden == 1) or (channel.type == interactions.ChannelType.DM):
                return
            else:
                if user.discriminator == "0":
                    em = interactions.Embed(
                        title="🗑️・Message supprimé",
                        description=f"Le message de **{user.username}** dans le salon **{channel.name}** ({channel.id}) sur **{guild.name}** ({guild.id}) vient d'être supprimé.",
                        color=0xFF5A5A,
                        timestamp=interactions.Timestamp.utcnow()
                    )
                else:
                    em = interactions.Embed(
                        title="🗑️・Message supprimé",
                        description=f"Le message de **{user.username}#{user.discriminator}** dans le salon **{channel.name}** ({channel.id}) sur **{guild.name}** ({guild.id}) vient d'être supprimé.",
                        color=0xFF5A5A,
                        timestamp=interactions.Timestamp.utcnow()
                    )
                if message.content != '':
                    em.add_field(name="**Message : **", value=content)
                if message.attachments is not None:
                    i: int = 0
                    for _ in message.attachments:
                        em.add_field(name=f"**Attachment {i + 1} (type : {message.attachments[i].content_type}): **",
                                     value=message.attachments[i].url)
                        i += 1
                em.set_footer(text=f"User ID : {user.id} | Message ID : {message.id}")

                return await logs_delete.send(embeds=em)
