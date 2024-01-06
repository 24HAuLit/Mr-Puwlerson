from interactions import Extension, Client, slash_command, SlashContext, LocalizedName, LocalizedDesc
from random import choice


class PileFace(Extension):
    def __int__(self, bot):
        self.bot: Client = bot

    @slash_command(
        name=LocalizedName(english_us="coinflip", french="pileface"),
        description=LocalizedDesc(english_us="Flip a coin and show the result", french="Lance une pièce et affiche le résultat"),
    )
    async def coinflip(self, ctx: SlashContext):
        element = ["pile", "face"]
        await ctx.send(f"La pièce est tombé sur **{choice(element)}**")
