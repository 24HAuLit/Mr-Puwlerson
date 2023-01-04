import sqlite3
import interactions
from const import DATA


class UnClaimCommand(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    async def unclaim(self, ctx: interactions.CommandContext):
        """Pour pouvoir retirer sa revendication d'un ticket."""

        guild = await interactions.get(self.bot, interactions.Guild, object_id=419529681885331456)
        channels = interactions.search_iterable(await guild.get_all_channels(),
                                                lambda c: c.parent_id == 1027647411495129109)
        channel = await ctx.get_channel()

        if DATA["roles"]["Staff"] in ctx.author.roles or DATA["roles"]["Owner"] in ctx.author.roles:

            # Partie Database
            conn = sqlite3.connect('./Database/puwlerson.db')
            cur = conn.cursor()
            cur.execute(f'SELECT * from ticket WHERE channel_id = {int(channel.id)}')
            row = cur.fetchone()

            if channel in channels:
                if int(ctx.author.id) == row[2]:
                    cur.execute(f"UPDATE ticket SET staff_id = 'None' WHERE channel_id = {int(channel.id)}")
                    conn.commit()
                    em = interactions.Embed(
                        description=f"Le ticket n'est plus pris en charge par {ctx.author.mention}.",
                        color=0xFF4646
                    )
                    await ctx.send(embeds=em)
                else:
                    await ctx.send("Vous ne pouvez pas faire cela car vous n'avez pas revendiqué le ticket.",
                                   ephemeral=True)
            else:
                await ctx.send("Vous ne pouvez pas utiliser cette commande dans ce salon.", ephemeral=True)
            conn.close()
        else:
            await ctx.send(":x: Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            interactions.StopCommand()


def setup(bot):
    UnClaimCommand(bot)
