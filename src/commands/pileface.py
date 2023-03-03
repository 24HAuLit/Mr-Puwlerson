from interactions import Extension, Client, extension_command, CommandContext
from random import choice


class PileFace(Extension):
    def __int__(self, bot):
        self.bot: Client = bot

    @extension_command()
    async def pileface(self, ctx: CommandContext):
        """Lance une pièce et affiche le résultat"""
        element = ["pile", "face"]
        await ctx.send(f"La pièce est tombé sur **{choice(element)}**")


def setup(bot):
    PileFace(bot)
