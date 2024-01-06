import sqlite3
import interactions
from src.listeners.ticket.components.close import ticket_close, ticket_close_reason
from src.utils.checks import database_exists, is_staff
from src.utils.message_config import ErrorMessage


class ClaimTicket(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.component_callback("claim_ticket")
    async def button_claim(self, ctx: interactions.ComponentContext):
        if await database_exists(ctx) is not True:
            return

        if await is_staff(ctx) is not True:
            return

        channel = ctx.channel
        id_staff = ctx.author.id
        guild = ctx.guild

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
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