import sqlite3
import interactions
from const import DATA
from src.listeners.ticket.components.close import ticket_close, ticket_close_reason


class ClaimTicket(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("claim_ticket")
    async def button_claim(self, ctx):
        channel = await ctx.get_channel()
        id_staff = ctx.author.id

        if DATA["roles"]["Staff"] in ctx.author.roles or DATA["roles"]["Owner"] in ctx.author.roles:
            # Partie database
            conn = sqlite3.connect('./Database/puwlerson.db')
            c = conn.cursor()
            c.execute(f"UPDATE ticket SET staff_id = {id_staff} WHERE channel_id = {int(channel.id)}")
            conn.commit()
            conn.close()

            # Partie message
            await ctx.message.edit(components=[ticket_close(), ticket_close_reason()])
            em = interactions.Embed(
                description=f"Le ticket a été pris en charge par {ctx.author.mention}.",
                color=0x2ECC70
            )
            await ctx.send(embeds=em)
        else:
            await ctx.send(":x: Vous n'avez pas la permission de faire ceci.", ephemeral=True)


def setup(bot):
    ClaimTicket(bot)
