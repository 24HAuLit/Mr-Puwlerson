import interactions
import random


class PileFace(interactions.Extension):
    def __int__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    async def pileface(self, ctx: interactions.CommandContext):
        list = ["pile", "face"]
        await ctx.send(f"La pièce est tombé sur **{random.choice(list)}**")


def setup(bot):
    PileFace(bot)
