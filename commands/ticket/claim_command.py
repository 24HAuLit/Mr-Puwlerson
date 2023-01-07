import sqlite3
import interactions
from const import DATA


class ClaimCommand(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    async def claim(self, ctx: interactions.CommandContext):
        """Pour pouvoir revendiquer un ticket."""

        if DATA["roles"]["Staff"] in ctx.author.roles or DATA["roles"]["Owner"] in ctx.author.roles:
            guild = await interactions.get(self.bot, interactions.Guild, object_id=DATA["main"]["guild"])
            channels = interactions.search_iterable(await guild.get_all_channels(),
                                                    lambda c: c.parent_id == DATA["main"]["ticket"])
            channel = await ctx.get_channel()
            id_staff = ctx.author.id

            # Partie Database
            conn = sqlite3.connect('./Database/puwlerson.db')
            cur = conn.cursor()
            cur.execute(f'SELECT * from ticket WHERE channel_id = {int(channel.id)}')
            row = cur.fetchone()

            # Partie commande
            if channel in channels:
                if row[2] is None or row[2] == 'None':
                    cur.execute(f"UPDATE ticket SET staff_id = {id_staff} WHERE channel_id = {int(channel.id)}")

                    conn.commit()
                    em = interactions.Embed(
                        description=f"Le ticket a été pris en charge par {ctx.author.mention}.",
                        color=0x2ECC70
                    )
                    await ctx.send(embeds=em)
                else:
                    await ctx.send(f"<@{row[2]}> a déjà pris en charge ce ticket.", ephemeral=True)
                conn.close()
            else:
                await ctx.send("Vous ne pouvez pas utiliser cette commande dans ce salon.", ephemeral=True)
        else:
            await ctx.send(":x: Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            interactions.StopCommand()


def setup(bot):
    ClaimCommand(bot)
