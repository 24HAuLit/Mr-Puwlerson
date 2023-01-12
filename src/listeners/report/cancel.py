import interactions


class CancelReport(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("cancel")
    async def report_cancel(self, ctx):
        await ctx.edit(components=[])
        await ctx.send("Vous avez annulé votre report.")


def setup(bot):
    CancelReport(bot)
