import interactions
from const import DATA
from src.listeners.ticket.components.close import confirm_close


class CloseTicket(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("close_ticket")
    async def button_close(self, ctx):
        if DATA["roles"]["Staff"] in ctx.author.roles or DATA["roles"]["Owner"] in ctx.author.roles:
            await ctx.send("Êtes-vous sur de vouloir fermer ce ticket ?", components=confirm_close(), ephemeral=True)
        else:
            await ctx.send(":x: Vous n'avez pas la permission de faire ceci.", ephemeral=True)


def setup(bot):
    CloseTicket(bot)
