import asyncio
import interactions
from random import choice
from time import time
from const import DATA


class Giveaway(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.button = interactions.Button(
            label="Participer",
            style=interactions.ButtonStyle.SUCCESS,
            custom_id="giveaway"
        )
        self.dic = {}
        self.check = False

    @interactions.extension_command()
    @interactions.option(description="Quel sera le cadeau ?")
    @interactions.option(description="Combien de temps durera le giveaway ? (en secondes)")
    async def giveaway(self, ctx: interactions.CommandContext, gift: str, seconds: int):
        """Crée un giveaway."""

        # Permission check
        if DATA["roles"]["Admin"] in ctx.author.roles or DATA["roles"]["Owner"] in ctx.author.roles:
            # Check si un giveaway est déjà en cours
            if self.check:
                return await ctx.send("Un giveaway est déjà en cours !", ephemeral=True)

            timestamp = time() + seconds
            channel = await interactions.get(self.bot, interactions.Channel, object_id=DATA["main"]["giveaway"])

            # Giveaway starting
            self.check = True
            em = interactions.Embed(
                title="Nouveau Giveaway ! 🎊",
                description=f"Un giveaway a été lancé par {ctx.author.mention} !\n*Cliquez sur le bouton ci-dessous pour participer.*",
                color=0x00FFC8
            )
            em.add_field(name="Gain", value=gift)
            em.add_field(name="Date de fin", value=f"<t:{int(timestamp)}:R>")
            await ctx.send("Le giveaway a bien été lancé !", ephemeral=True)
            message = await channel.send(embeds=em, components=[self.button])

            # Giveaway ending
            await asyncio.sleep(seconds)
            winner = choice(list(self.dic.keys()))
            user = await interactions.get(self.bot, interactions.User, object_id=winner)

            em_end = interactions.Embed(
                title="Nouveau Giveaway ! 🎊",
                description=f"Le giveaway lancé par {ctx.author.mention} est terminé ! ",
                color=0x75FD75
            )
            em_end.add_field(name="Gain", value=gift)
            em_end.add_field(name="Gagnant", value=user.mention)

            await message.edit(embeds=em_end, components=[])

            await channel.send(f"Le giveaway est terminé ! Le gagnant est {user.mention} !")
            self.dic.clear()
            self.check = False
        else:
            await ctx.send("Vous n'avez pas la permission de faire cela !", ephemeral=True)
            return interactions.StopCommand()

    @interactions.extension_component("giveaway")
    async def on_button_click(self, ctx: interactions.ComponentContext):
        if DATA["roles"]["Admin"] in ctx.author.roles or DATA["roles"]["Owner"] in ctx.author.roles:
            return await ctx.send("Vous ne pouvez pas participer au giveaway !", ephemeral=True)
        if ctx.author.id not in self.dic:
            self.dic[ctx.author.id] = 1
            return await ctx.send(f"Vous participez désormais au giveaway !", ephemeral=True)
        else:
            self.dic.pop(ctx.author.id)
            return await ctx.send(f"Vous ne participez plus au giveaway !", ephemeral=True)


def setup(bot):
    Giveaway(bot)
