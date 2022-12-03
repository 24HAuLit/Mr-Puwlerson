import interactions
from const import DATA


class Rename(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    @interactions.option("Nouveau nom pour le ticket")
    async def rename(self, ctx: interactions.CommandContext, nom: str):
        """Pour pouvoir renommer un ticket."""

        guild = await interactions.get(self.bot, interactions.Guild, object_id=DATA["principal"]["guild"])
        channels = interactions.search_iterable(await guild.get_all_channels(),
                                                lambda c: c.parent_id == 1027647411495129109)
        if DATA["roles"]["Staff"] in ctx.author.roles or DATA["roles"]["Owner"] in ctx.author.roles:
            if ctx.channel in channels:
                await ctx.channel.modify(name=nom)
                await ctx.send(f"Le ticket vient d'être renommé **{nom}**.", ephemeral=True)
            else:
                await ctx.send("Vous ne pouvez pas utiliser cette commande dans ce salon.", ephemeral=True)
        else:
            await ctx.send(":x: Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            interactions.StopCommand()


def setup(bot):
    Rename(bot)
