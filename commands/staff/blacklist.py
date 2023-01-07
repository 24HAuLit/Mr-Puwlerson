import sqlite3
from datetime import datetime
import interactions
from const import DATA


class Blacklist(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    @interactions.option("Membre à blacklist")
    @interactions.option("Raison du blacklist")
    async def blacklist(self, ctx: interactions.CommandContext, user: interactions.User, reason: str):
        """Pour pouvoir blacklist un membre des reports et des suggestions."""

        if DATA["roles"]["Admin"] in ctx.author.roles or DATA["roles"]["Owner"] in ctx.author.roles:
            user_id = user.id
            channel = await interactions.get(self.bot, interactions.Channel, object_id=DATA["main"]["staff_logs"])
            dm = user_id

            conn = sqlite3.connect('./Database/puwlerson.db')
            c = conn.cursor()
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
            em_dm.set_footer(icon_url=ctx.author.get_avatar_url(), text=f"Staff : {ctx.author.username}#{ctx.author.discriminator} ({ctx.author.id})")
            await user.send(embeds=em_dm)

        else:
            await ctx.send(":x: Vous n'avez pas la permission d'utiliser cette commande'.", ephemeral=True)
            interactions.StopCommand()


def setup(bot):
    Blacklist(bot)
