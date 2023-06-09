import os
import sqlite3
import interactions
from message_config import ErrorMessage
from datetime import datetime


class Blacklist(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(dm_permission=False)
    @interactions.option("Membre à blacklist")
    @interactions.option("Raison du blacklist")
    async def blacklist(self, ctx: interactions.CommandContext, user: interactions.User, reason: str):
        """Pour pouvoir blacklist un membre des reports et des suggestions."""
        guild = await ctx.get_guild()

        if os.path.exists(f"./Database/{guild.id}.db") is False:
            return await ctx.send(ErrorMessage.database_not_found(guild.id), ephemeral=True)

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if c.execute("SELECT id FROM roles WHERE type = 'Admin'").fetchone()[0] in ctx.author.roles or \
                c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles:
            user_id = user.id
            channel = await interactions.get(self.bot, interactions.Channel,
                                             object_id=c.execute(
                                                 "SELECT id FROM logs_channels WHERE name = 'blacklist'").fetchone()[0])

            c.execute("INSERT INTO blacklist VALUES (NULL, '{}', '{}')".format(user_id, reason))
            conn.commit()
            conn.close()

            await ctx.send(f"{user.mention} ({user.id}) a bien été blacklist.", ephemeral=True)

            if ctx.author.discriminator == "0":
                if user.discriminator == "0":
                    em = interactions.Embed(
                        description=f"Le membre {user.username} a été blacklist par {ctx.author.username} pour la raison {reason}",
                        color=0xFF0000,
                        timestamp=datetime.utcnow()
                    )
                else:
                    em = interactions.Embed(
                        description=f"Le membre {user.username}#{user.discriminator} a été blacklist par {ctx.author.username} pour la raison {reason}",
                        color=0xFF0000,
                        timestamp=datetime.utcnow()
                    )
            else:
                if user.discriminator == "0":
                    em = interactions.Embed(
                        description=f"Le membre {user.username} a été blacklist par {ctx.author.username}#{ctx.author.discriminator} pour la raison {reason}",
                        color=0xFF0000,
                        timestamp=datetime.utcnow()
                    )
                else:
                    em = interactions.Embed(
                        description=f"Le membre {user.username}#{user.discriminator} a été blacklist par {ctx.author.username}#{ctx.author.discriminator} pour la raison {reason}",
                        color=0xFF0000,
                        timestamp=datetime.utcnow()
                    )
            em.set_footer(text=f"Staff ID : {ctx.author.id} | User ID : {user_id}")

            await channel.send(embeds=em)

            if ctx.author.discriminator == "0":
                em_dm = interactions.Embed(
                    title="🔒・Blacklist",
                    description=f"Vous avez été blacklist par **{ctx.author.username}** pour **{reason}**.\nVous pourrez être unblacklist si vous êtes gentil ou après un certain temps.",
                    color=0xFF0000,
                    timestamp=datetime.utcnow()
                )
                em_dm.set_footer(icon_url=ctx.author.get_avatar_url(),
                                 text=f"Staff : {ctx.author.username} ({ctx.author.id})")
            else:
                em_dm = interactions.Embed(
                    title="🔒・Blacklist",
                    description=f"Vous avez été blacklist par **{ctx.author.username}#{ctx.author.discriminator}** pour **{reason}**.\nVous pourrez être unblacklist si vous êtes gentil ou après un certain temps.",
                    color=0xFF0000,
                    timestamp=datetime.utcnow()
                )
                em_dm.set_footer(icon_url=ctx.author.get_avatar_url(),
                                 text=f"Staff : {ctx.author.username}#{ctx.author.discriminator} ({ctx.author.id})")

            await user.send(embeds=em_dm)

        else:
            await ctx.send(ErrorMessage.MissingPermissions(guild.id), ephemeral=True)
            return interactions.StopCommand()


def setup(bot):
    Blacklist(bot)
