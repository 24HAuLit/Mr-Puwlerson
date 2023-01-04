import interactions


class Ping(interactions.Extension):

    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(
        name="ping",
        description="Pong!",
        dm_permission=False
    )
    async def command(self, ctx: interactions.CommandContext):
        await ctx.send(f"Pong!\nLa latence du bot est de **{abs(round(self.bot.latency))}ms**.", ephemeral=True)


def setup(bot):
    Ping(bot)
