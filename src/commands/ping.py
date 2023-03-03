from interactions import Extension, Client, extension_command, CommandContext


class Ping(Extension):

    def __init__(self, bot):
        self.bot: Client = bot

    @extension_command()
    async def ping(self, ctx: CommandContext):
        """Pong!"""
        await ctx.send(f"Pong!\nLa latence du bot est de **{abs(round(self.bot.latency))}ms**.", ephemeral=True)


def setup(bot):
    Ping(bot)
