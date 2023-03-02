import os
import sqlite3
from datetime import datetime
import interactions


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
            return await ctx.send("Ce serveur n'est pas encore configuré.", ephemeral=True)

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if c.execute("SELECT id FROM roles WHERE type = 'Admin'").fetchone()[0] in ctx.author.roles or c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles:
            user_id = user.id
            channel = await interactions.get(self.bot, interactions.Channel,
                                             object_id=c.execute("SELECT id FROM logs_channels WHERE name = 'blacklist'").fetchone()[0])

            c.execute("INSERT INTO blacklist VALUES (NULL, '{}', '{}')".format(user_id, reason))
            conn.commit()
            conn.close()

            await ctx.send(f"{user.mention} ({user.id}) a bien été blacklist.", ephemeral=True)
            em = interactions.Embed(
                description=f"Le membre {user.username}#{user.discriminator} a été blacklist par {ctx.author.username}#{ctx.author.discriminator} pour la raison {reason}",
                color=0xFF0000,
                timestamp=datetime.utcnow()
            )
            em.set_footer(text=f"Staff ID : {ctx.author.id} | User ID : {user_id}")

            await channel.send(embeds=em)

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
            await ctx.send(":x: Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            interactions.StopCommand()


def setup(bot):
    Blacklist(bot)
