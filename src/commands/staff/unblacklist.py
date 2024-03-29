import os
import sqlite3
import interactions
from message_config import ErrorMessage
from datetime import datetime


class UnBlacklist(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(dm_permission=False)
    @interactions.option("Membre à unblacklist")
    @interactions.option("Raison du unblacklist", required=False)
    async def unblacklist(self, ctx: interactions.CommandContext, user: interactions.User,
                          reason: str = "Aucune raison"):
        """Pour pouvoir unblacklist un membre."""
        guild = await ctx.get_guild()

        if os.path.exists(f"./Database/{guild.id}.db") is False:
            return await ctx.send(ErrorMessage.database_not_found(guild.id), ephemeral=True)

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles or \
                c.execute("SELECT id FROM roles WHERE type = 'Admin'").fetchone()[0] in ctx.author.roles:
            user_id = user.id
            reason = reason
            channel = await interactions.get(self.bot, interactions.Channel, object_id=
            c.execute("SELECT id FROM logs_channels WHERE name = 'blacklist'").fetchone()[0])

            c.execute("DELETE FROM blacklist WHERE user_id='{}'".format(user_id))
            conn.commit()

            await ctx.send(f"{user.mention} ({user.id}) a bien été unblacklist.", ephemeral=True)

            if user.discriminator == "0":
                em = interactions.Embed(
                    description=f"Le membre {user.username} a été unblacklist par {ctx.author.username}#{ctx.author.discriminator}",
                    color=0x00FF00,
                    timestamp=datetime.utcnow()
                )
            else:
                em = interactions.Embed(
                    description=f"Le membre {user.username}#{user.discriminator} a été unblacklist par {ctx.author.username}#{ctx.author.discriminator}",
                    color=0x00FF00,
                    timestamp=datetime.utcnow()
                )
            em.set_footer(text=f"Staff ID : {ctx.author.id} | User ID : {user.id}")

            await channel.send(embeds=em)

            if ctx.author.discriminator == "0":
                em_dm = interactions.Embed(
                    title="🔓・Unblacklist",
                    description=f"Vous avez été unblacklist par **{ctx.author.username}** pour **{reason}**.\nVous "
                                f"avez été gentil, c'est bien, maintenant continuer sur cette voie.",
                    color=0x00FF00,
                    timestamp=datetime.utcnow()
                )
                em_dm.set_footer(icon_url=ctx.author.get_avatar_url(),
                                 text=f"Staff : {ctx.author.username} ({ctx.author.id})")
            else:
                em_dm = interactions.Embed(
                    title="🔓・Unblacklist",
                    description=f"Vous avez été unblacklist par **{ctx.author.username}#{ctx.author.discriminator}** "
                                f"pour **{reason}**.\nVous avez été gentil, c'est bien, maintenant continuer sur "
                                f"cette voie.",
                    color=0x00FF00,
                    timestamp=datetime.utcnow()
                )
                em_dm.set_footer(icon_url=ctx.author.get_avatar_url(),
                                 text=f"Staff : {ctx.author.username}#{ctx.author.discriminator} ({ctx.author.id})")
            await user.send(embeds=em_dm)

        else:
            await ctx.send(ErrorMessage.MissingPermissions(guild.id), ephemeral=True)
            return interactions.StopCommand()

        conn.close()


def setup(bot):
    UnBlacklist(bot)
