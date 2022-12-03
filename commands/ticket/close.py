import interactions
from interactions.ext.checks import has_role
from listeners.ticket.components.close import confirm_close


class CloseTicketCommand(interactions.Extension):

    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(
        name="close",
        description="Pour pouvoir fermer le ticket."
    )
    @has_role(1018602650566139984, 419532166888816640)
    async def close(self, ctx: interactions.CommandContext):
        guild = await interactions.get(self.bot, interactions.Guild, object_id=419529681885331456)
        channels = interactions.search_iterable(await guild.get_all_channels(),
                                                lambda c: c.parent_id == 1027647411495129109)
        if ctx.channel in channels:
            await ctx.send("Êtes-vous sur de vouloir fermer ce ticket ?", components=confirm_close(), ephemeral=True)
        else:
            await ctx.send("Vous ne pouvez pas utiliser cette commande dans ce salon.", ephemeral=True)


def setup(bot):
    CloseTicketCommand(bot)
