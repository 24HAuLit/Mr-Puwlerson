import interactions
from interactions.ext.checks import has_role
from listeners.ticket.components.close import confirm_close


class CloseTicket(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("close_ticket")
    @has_role(1018602650566139984, 419532166888816640)
    async def button_close(self, ctx):
        await ctx.send("Êtes-vous sur de vouloir fermer ce ticket ?", components=confirm_close(), ephemeral=True)


def setup(bot):
    CloseTicket(bot)
