import sqlite3
from datetime import datetime
import interactions
from const import DATA


class UnBlacklist(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    @interactions.option("Membre à unblacklist")
    @interactions.option("Raison du unblacklist", required=False)
    async def unblacklist(self, ctx: interactions.CommandContext, user: interactions.User, reason: str = None):
        if DATA["roles"]["Admin"] in ctx.author.roles or DATA["roles"]["Owner"] in ctx.author.roles:
            user_id = user.id
            reason = reason
            channel = await interactions.get(self.bot, interactions.Channel, object_id=1060273879018381405)

            conn = sqlite3.connect('./Database/puwlerson.db')
            c = conn.cursor()
            c.execute("DELETE FROM blacklist WHERE user_id='{}'".format(user_id))
            conn.commit()
            conn.close()

            await ctx.send(f"{user.mention} ({user.id}) a bien été unblacklist.", ephemeral=True)
            em = interactions.Embed(
                description=f"Le membre {user.username}#{user.discriminator} a été unblacklist par {ctx.author.username}#{ctx.author.discriminator}",
                color=0x00FF00,
                timestamp=datetime.utcnow()
            )
            em.set_footer(text=f"Staff ID : {ctx.author.id} | User ID : {user.id}")

            await channel.send(embeds=em)
        else:
            await ctx.send(":x: Vous n'avez pas la permission d'utiliser cette commande'.", ephemeral=True)
            interactions.StopCommand()


def setup(bot):
    UnBlacklist(bot)
