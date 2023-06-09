import os
import sqlite3
import interactions
from datetime import datetime


class JoinQuit(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_listener(name="on_guild_member_add")
    async def join(self, user: interactions.GuildMember):
        guild = await interactions.get(self.bot, interactions.Guild, object_id=int(user.guild_id))

        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        logs = await interactions.get(self.bot, interactions.Channel, object_id=c.execute("SELECT id FROM logs_channels WHERE name = 'join-quit'").fetchone()[0])

        if user.discriminator == "0":
            em = interactions.Embed(
                title="🛬・Un utilisateur a rejoint un serveur",
                description=f"**{user.username}** a rejoint **{guild.name}**",
                color=0x4CFF4C,
                timestamp=datetime.utcnow()
            )
            em.set_footer(text=f"Server ID : {guild.id} | User ID : {user.id}")
            await logs.send(embeds=em)
        else:
            em = interactions.Embed(
                title="🛬・Un utilisateur a rejoint un serveur",
                description=f"**{user.username}#{user.discriminator}** a rejoint **{guild.name}**",
                color=0x4CFF4C,
                timestamp=datetime.utcnow()
            )
            em.set_footer(text=f"Server ID : {guild.id} | User ID : {user.id}")
            await logs.send(embeds=em)

        conn.close()

    @interactions.extension_listener(name="on_guild_member_remove")
    async def quit(self, user: interactions.GuildMember):
        guild = await interactions.get(self.bot, interactions.Guild, object_id=int(user.guild_id))

        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        logs = await interactions.get(self.bot, interactions.Channel, object_id=c.execute("SELECT id FROM logs_channels WHERE name = 'join-quit'").fetchone()[0])

        if user.discriminator == "0":
            em = interactions.Embed(
                title="🛫・Un utilisateur a quitté un serveur",
                description=f"**{user.username}** a quitté **{guild.name}**",
                color=0xFF5A5A,
                timestamp=datetime.utcnow()
            )
            em.set_footer(text=f"Server ID : {guild.id} | User ID : {user.id}")
            await logs.send(embeds=em)
        else:
            em = interactions.Embed(
                title="🛫・Un utilisateur a quitté un serveur",
                description=f"**{user.username}#{user.discriminator}** a quitté **{guild.name}**",
                color=0xFF5A5A,
                timestamp=datetime.utcnow()
            )
            em.set_footer(text=f"Server ID : {guild.id} | User ID : {user.id}")
            await logs.send(embeds=em)

        conn.close()


def setup(bot):
    JoinQuit(bot)
