from interactions import Extension, Client, slash_command, SlashContext


class Ping(Extension):
    def __init__(self, bot):
        self.bot: Client = bot

    @slash_command()
    async def ping(self, ctx: SlashContext):
        """Pong!"""
        await ctx.send(f"Pong! ({round(self.bot.latency * 1000)}ms)", ephemeral=True)
