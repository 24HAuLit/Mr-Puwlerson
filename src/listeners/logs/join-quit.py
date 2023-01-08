import interactions
from datetime import datetime

from const import DATA


class JoinQuit(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_listener(name="on_guild_member_add")
    async def join(self, user: interactions.GuildMember):
        join = await interactions.get(self.bot, interactions.Channel, object_id=DATA["logs"]["global"]["join"])
        guild = await interactions.get(self.bot, interactions.Guild, object_id=int(user.guild_id))

        em = interactions.Embed(
            title="🛬 Un utilisateur a rejoint un serveur",
            description=f"**{user.username}#{user.discriminator}** a rejoint **{guild.name}**",
            color=0x4CFF4C,
            timestamp=datetime.utcnow()
        )
        em.set_footer(text=f"Server ID : {guild.id} | User ID : {user.id}")
        await join.send(embeds=em)

    @interactions.extension_listener(name="on_guild_member_remove")
    async def quit(self, user: interactions.GuildMember):
        quit = await interactions.get(self.bot, interactions.Channel, object_id=DATA["logs"]["global"]["leave"])
        guild = await interactions.get(self.bot, interactions.Guild, object_id=int(user.guild_id))

        em = interactions.Embed(
            title="🛫 Un utilisateur a quitté un serveur",
            description=f"**{user.username}#{user.discriminator}** a quitté **{guild}**",
            color=0xFF5A5A,
            timestamp=datetime.utcnow()
        )
        em.set_footer(text=f"Server ID : {guild.id} | User ID : {user.id}")

        await quit.send(embeds=em)


def setup(bot):
    JoinQuit(bot)
