import interactions
from src.utils.checks import database_exists, is_staff
from src.listeners.ticket.components.close import confirm_close_cmd


class CloseTicket(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.component_callback("close_ticket")
    async def button_close(self, ctx: interactions.ComponentContext):
        if await database_exists(ctx) is not True:
            return

        if await is_staff(ctx) is not True:
            return

        await ctx.send("Êtes-vous sur de vouloir fermer ce ticket ?", components=confirm_close_cmd(), ephemeral=True)
