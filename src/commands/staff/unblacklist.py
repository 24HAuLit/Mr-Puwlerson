import sqlite3
from datetime import datetime
import interactions
from const import DATA


class UnBlacklist(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(dm_permission=False)
    @interactions.option("Membre à unblacklist")
    @interactions.option("Raison du unblacklist", required=False)
    async def unblacklist(self, ctx: interactions.CommandContext, user: interactions.User, reason: str = "Aucune raison"):
        """Pour pouvoir unblacklist un membre."""
        guild = await ctx.get_guild()
        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles or \
                c.execute("SELECT id FROM roles WHERE type = 'Admin'").fetchone()[0] in ctx.author.roles:
            user_id = user.id
            reason = reason
            channel = await interactions.get(self.bot, interactions.Channel, object_id=DATA["logs"]["moderation"]["blacklist"])

            c.execute("DELETE FROM blacklist WHERE user_id='{}'".format(user_id))
            conn.commit()

            await ctx.send(f"{user.mention} ({user.id}) a bien été unblacklist.", ephemeral=True)
            em = interactions.Embed(
                description=f"Le membre {user.username}#{user.discriminator} a été unblacklist par {ctx.author.username}#{ctx.author.discriminator}",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            em.set_footer(text=f"Staff ID : {ctx.author.id} | User ID : {user.id}")

            await channel.send(embeds=em)

            em_dm = interactions.Embed(
                title="🔓・Unblacklist",
                description=f"Vous avez été unblacklist par **{ctx.author.username}#{ctx.author.discriminator}** pour"
                            f" **{reason}**.\nVous avez été gentil, c'est bien, maintenant continuer sur cette voie.",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            em_dm.set_footer(icon_url=ctx.author.get_avatar_url(),
                             text=f"Staff : {ctx.author.username}#{ctx.author.discriminator} ({ctx.author.id})")
            await user.send(embeds=em_dm)

        else:
            await ctx.send(":x: Vous n'avez pas la permission d'utiliser cette commande'.", ephemeral=True)
            interactions.StopCommand()

        conn.close()


def setup(bot):
    UnBlacklist(bot)
