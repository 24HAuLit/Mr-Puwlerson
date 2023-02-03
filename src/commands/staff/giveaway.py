import interactions
from time import time


class Giveaway(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.button = interactions.Button(
            label="Participer",
            style=interactions.ButtonStyle.PRIMARY,
            custom_id="giveaway"
        )
        self.dic = {}

    @interactions.extension_command()
    @interactions.option(description="Quel sera le cadeau ?")
    @interactions.option(description="Combien de temps durera le giveaway ? (en secondes)")
    async def giveaway(self, ctx, gift: str, seconds: int):
        """Crée un giveaway."""
        timestamp = time() + seconds

        em = interactions.Embed(
            title="Giveaway",
            description=f"Un giveaway a été lancé par {ctx.author.mention} !",
            color=0x00FF00
        )
        em.add_field(name="Gain", value=gift)
        em.add_field(name="Date de fin", value=f"<t:{int(timestamp)}:R>")
        await ctx.send(embeds=em, components=[self.button])

    @interactions.extension_component("giveaway")
    async def on_button_click(self, ctx):
        if ctx.author.id not in self.dic:
            self.dic[ctx.author.id] = 1
            await ctx.send(f"Vous participez au giveaway !", ephemeral=True)
        else:
            await ctx.send(f"Vous participez déjà au giveaway !", ephemeral=True)


def setup(bot):
    Giveaway(bot)
