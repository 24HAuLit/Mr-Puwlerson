import interactions


class Ping(interactions.Extension):

    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    async def ping(self, ctx: interactions.CommandContext):
        """Pong!"""
        await ctx.send(f"Pong!\nLa latence du bot est de **{abs(round(self.bot.latency))}ms**.", ephemeral=True)


def setup(bot):
    Ping(bot)
