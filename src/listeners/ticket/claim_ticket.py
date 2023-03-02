import sqlite3
import interactions
from src.listeners.ticket.components.close import ticket_close, ticket_close_reason


class ClaimTicket(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("claim_ticket")
    async def button_claim(self, ctx):
        channel = await ctx.get_channel()
        id_staff = ctx.author.id
        guild = await ctx.get_guild()
        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if c.execute("SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0] in ctx.author.roles or c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles:
            c.execute(f"UPDATE ticket SET staff_id = {id_staff} WHERE channel_id = {int(channel.id)}")

            # Partie message
            await ctx.message.edit(components=[ticket_close(), ticket_close_reason()])
            em = interactions.Embed(
                description=f"Le ticket a été pris en charge par {ctx.author.mention}.",
                color=0x2ECC70
            )
            await ctx.send(embeds=em)
        else:
            await ctx.send(":x: Vous n'avez pas la permission de faire ceci.", ephemeral=True)

        conn.commit()
        conn.close()


def setup(bot):
    ClaimTicket(bot)
