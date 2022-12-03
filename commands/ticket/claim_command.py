import sqlite3
import interactions
from interactions.ext.checks import has_role


class ClaimCommand(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(
        name="claim",
        description="Pour pouvoir revendiquer un ticket"
    )
    @has_role(1018602650566139984, 419532166888816640)
    async def claim_command(self, ctx: interactions.CommandContext):
        guild = await interactions.get(self.bot, interactions.Guild, object_id=419529681885331456)
        channels = interactions.search_iterable(await guild.get_all_channels(),
                                                lambda c: c.parent_id == 1027647411495129109)
        channel = await ctx.get_channel()
        id_staff = ctx.author.id

        # Partie Database
        conn = sqlite3.connect('./Database/ticket.db')
        cur = conn.cursor()
        cur.execute(f'SELECT * from table_name WHERE channel_id = {int(channel.id)}')
        row = cur.fetchone()

        # Partie commande
        if channel in channels:
            if row[2] is None or row[2] == 'None':
                cur.execute(f"UPDATE table_name SET staff_id = {id_staff} WHERE channel_id = {int(channel.id)}")
                conn.commit()
                em = interactions.Embed(
                    description=f"Le ticket a été pris en charge par {ctx.author.mention}.",
                    color=0x2ECC70
                )
                await ctx.send(embeds=em)
            else:
                await ctx.send(f"<@{row[2]}> a déjà pris en charge ce ticket.", ephemeral=True)
        else:
            await ctx.send("Vous ne pouvez pas utiliser cette commande dans ce salon.", ephemeral=True)

        conn.close()


def setup(bot):
    ClaimCommand(bot)
