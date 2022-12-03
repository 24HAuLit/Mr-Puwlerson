import interactions
from interactions.ext.checks import has_role


class Rename(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(
        name="rename",
        description="Pour pouvoir renommer un ticket."
    )
    @interactions.option(
        type=interactions.OptionType.STRING,
        name="nom",
        description="Nouveau nom pour le ticket",
        required=True
    )
    @has_role(1018602650566139984, 419532166888816640)
    async def _rename(self, ctx: interactions.CommandContext, nom):
        guild = await interactions.get(self.bot, interactions.Guild, object_id=419529681885331456)
        channels = interactions.search_iterable(await guild.get_all_channels(),
                                                lambda c: c.parent_id == 1027647411495129109)
        if ctx.channel in channels:
            await ctx.channel.modify(name=nom)
            await ctx.send(f"Le ticket vient d'être renommé **{nom}**.", ephemeral=True)
        else:
            await ctx.send("Vous ne pouvez pas utiliser cette commande dans ce salon.", ephemeral=True)


def setup(bot):
    Rename(bot)
