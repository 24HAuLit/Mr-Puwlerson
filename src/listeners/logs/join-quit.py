import os
import sqlite3
import interactions
from interactions.api.events import MemberAdd, MemberRemove


class JoinQuit(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.listen(MemberAdd)
    async def join(self, user: MemberAdd):
        if os.path.exists(f'./Database/{user.guild.id}.db') is False:
            return

        conn = sqlite3.connect(f'./Database/{user.guild.id}.db')
        c = conn.cursor()

        logs = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'join-quit'").fetchone()[0])

        if user.member.discriminator == "0":
            em = interactions.Embed(
                title="🛬・Un utilisateur a rejoint un serveur",
                description=f"**{user.member.username}** a rejoint **{user.guild.name}**",
                color=0x4CFF4C,
                timestamp=interactions.Timestamp.utcnow()
            )
            em.set_footer(text=f"Server ID : {user.guild.id} | User ID : {user.member.id}")
            await logs.send(embeds=em)
        else:
            em = interactions.Embed(
                title="🛬・Un utilisateur a rejoint un serveur",
                description=f"**{user.member.username}#{user.member.discriminator}** a rejoint **{user.guild.name}**",
                color=0x4CFF4C,
                timestamp=interactions.Timestamp.utcnow()
            )
            em.set_footer(text=f"Server ID : {user.guild.id} | User ID : {user.member.id}")
            await logs.send(embeds=em)

        conn.close()

    @interactions.listen(MemberRemove)
    async def quit(self, user: MemberRemove):
        if os.path.exists(f'./Database/{user.guild.id}.db') is False:
            return

        conn = sqlite3.connect(f'./Database/{user.guild.id}.db')
        c = conn.cursor()

        logs = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'join-quit'").fetchone()[0])

        if user.member.discriminator == "0":
            em = interactions.Embed(
                title="🛫・Un utilisateur a quitté un serveur",
                description=f"**{user.member.username}** a quitté **{user.guild.name}**",
                color=0xFF5A5A,
                timestamp=interactions.Timestamp.utcnow()
            )
            em.set_footer(text=f"Server ID : {user.guild.id} | User ID : {user.member.id}")
            await logs.send(embeds=em)
        else:
            em = interactions.Embed(
                title="🛫・Un utilisateur a quitté un serveur",
                description=f"**{user.member.username}#{user.member.discriminator}** a quitté **{user.guild.name}**",
                color=0xFF5A5A,
                timestamp=interactions.Timestamp.utcnow()
            )
            em.set_footer(text=f"Server ID : {user.guild.id} | User ID : {user.member.id}")
            await logs.send(embeds=em)

        conn.close()
