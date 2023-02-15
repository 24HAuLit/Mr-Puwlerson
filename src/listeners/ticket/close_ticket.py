import sqlite3
import interactions
from src.listeners.ticket.components.close import confirm_close


class CloseTicket(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("close_ticket")
    async def button_close(self, ctx):
        guild = await ctx.get_guild()
        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()
        if c.execute("SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0] in ctx.author.roles or c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles:
            await ctx.send("Êtes-vous sur de vouloir fermer ce ticket ?", components=confirm_close(), ephemeral=True)
        else:
            await ctx.send(":x: Vous n'avez pas la permission de faire ceci.", ephemeral=True)


def setup(bot):
    CloseTicket(bot)
