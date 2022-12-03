import interactions
from const import DATA
from listeners.ticket.components.close import confirm_close


class CloseTicketCommand(interactions.Extension):

    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    async def close(self, ctx: interactions.CommandContext):
        """Pour pouvoir fermer le ticket."""
        if DATA["roles"]["Staff"] in ctx.author.roles or DATA["roles"]["Owner"] in ctx.author.roles:
            guild = await interactions.get(self.bot, interactions.Guild, object_id=DATA["principal"]["guild"])
            channels = interactions.search_iterable(await guild.get_all_channels(),
                                                    lambda c: c.parent_id == 1027647411495129109)
            if ctx.channel in channels:
                await ctx.send("Êtes-vous sur de vouloir fermer ce ticket ?", components=confirm_close(),
                               ephemeral=True)
            else:
                await ctx.send("Vous ne pouvez pas utiliser cette commande dans ce salon.", ephemeral=True)
        else:
            await ctx.send(":x: Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            interactions.StopCommand()


def setup(bot):
    CloseTicketCommand(bot)
