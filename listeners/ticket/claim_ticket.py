import sqlite3
import interactions
from interactions.ext.checks import has_role
from listeners.ticket.components.close import ticket_close, ticket_close_reason


class ClaimTicket(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("claim_ticket")
    @has_role(1018602650566139984, 419532166888816640)
    async def button_claim(self, ctx):
        channel = await ctx.get_channel()
        id_staff = ctx.author.id

        # Partie database
        conn = sqlite3.connect('./Database/ticket.db')
        c = conn.cursor()
        c.execute(f"UPDATE table_name SET staff_id = {id_staff} WHERE channel_id = {int(channel.id)}")
        conn.commit()
        conn.close()

        # Partie message
        await ctx.message.edit(components=[ticket_close(), ticket_close_reason()])
        em = interactions.Embed(
            description=f"Le ticket a été pris en charge par {ctx.author.mention}.",
            color=0x2ECC70
        )
        await ctx.send(embeds=em)


def setup(bot):
    ClaimTicket(bot)
