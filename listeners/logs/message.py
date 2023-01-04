import interactions
from datetime import datetime


class Message(interactions.Extension):

    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.banned_channels = [419560252984524800, 946022224857554985, 997376932272418836, 1019331289897238670,
                                419560554403725312, 419539020909903902]

    @interactions.extension_listener(name="on_message_create")
    async def new_message(self, message: interactions.Message):
        channel = await message.get_channel()
        content = message.content
        if message.guild_id is not None:
            guild = await message.get_guild()
        logs_create = await interactions.get(self.bot, interactions.Channel, object_id=1025130771456983080)

        if message.author.bot:
            return
        else:
            if (channel.id in self.banned_channels) or (channel.type == interactions.ChannelType.DM):
                return
            else:
                em = interactions.Embed(
                    title="Nouveau message",
                    url=message.url,
                    description=f"**{message.author.username}#{message.author.discriminator}** vient d'envoyer un message sur **{guild}** ({guild.id}) dans le salon **{channel}** ({channel.id})",
                    color=0x4CFF4C,
                    timestamp=datetime.utcnow()
                )
                if message.content != '':
                    em.add_field(name="**Message : **", value=content)
                if message.attachments is not None:
                    i: int = 0
                    for j in message.attachments:
                        em.add_field(name=f"**Attachment {i + 1} (type : {message.attachments[i].content_type}): **", value=message.attachments[i].url)
                        i += 1
                em.set_footer(text=f"Author ID : {message.author.id} | Message ID : {message.id}")

                await logs_create.send(embeds=em)

    @interactions.extension_listener(name="on_message_update")
    async def edit_message(self, before: interactions.Message, after: interactions.Message):
        old_content = before.content
        new_content = after.content
        channel = await after.get_channel()
        if after.guild_id is not None:
            guild = await after.get_guild()
        logs_edit = await interactions.get(self.bot, interactions.Channel, object_id=1025703859689103392)

        if before.author.bot:
            return
        else:
            if (channel.id in self.banned_channels) or (channel.type == interactions.ChannelType.DM):
                return
            else:
                em2 = interactions.Embed(
                    title="Modification de message",
                    url=after.url,
                    description=f"**{after.author.username}#{after.author.discriminator}** vient de modifier un message sur **{guild}** ({guild.id}) dans le salon **{channel}** ({channel.id})",
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
                        em2.add_field(name=f"**Ancien Attachment {i + 1} (type : {before.attachments[i].content_type}): **", value=before.attachments[i].url)
                        em2.add_field(name=f"**Nouveau Attachment {i + 1} (type : {after.attachments[i].content_type}): **", value=after.attachments[i].url)
                        i += 1
                em2.set_footer(text=f"Author ID : {after.author.id} | Message ID : {after.id}")

                await logs_edit.send(embeds=em2)

    @interactions.extension_listener(name="on_message_delete")
    async def message_delete(self, message: interactions.Message):
        user = message.author
        channel = await message.get_channel()
        content = message.content
        if message.guild_id is not None:
            guild = await message.get_guild()
        logs_delete = await interactions.get(self.bot, interactions.Channel, object_id=1025703875061219358)

        if message.author.bot:
            return
        else:
            if (channel.id in self.banned_channels) or (channel.type == interactions.ChannelType.DM):
                return
            else:
                em = interactions.Embed(
                    title="Message supprimé",
                    description=f"Le message de **{user.username}#{user.discriminator}** dans le salon **{channel}** ({channel.id}) sur **{guild}** ({guild.id}) vient d'être supprimé.",
                    color=0xFF5A5A,
                    timestamp=datetime.utcnow()
                )
                if message.content != '':
                    em.add_field(name="**Message : **", value=content)
                if message.attachments is not None:
                    i: int = 0
                    for j in message.attachments:
                        em.add_field(name=f"**Attachment {i + 1} (type : {message.attachments[i].content_type}): **", value=message.attachments[i].url)
                        i += 1
                em.set_footer(text=f"User ID : {user.id} | Message ID : {message.id}")

                await logs_delete.send(embeds=em)


def setup(bot):
    Message(bot)


