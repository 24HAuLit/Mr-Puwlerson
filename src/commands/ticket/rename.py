import interactions
from interactions import LocalizedName, LocalizedDesc
from src.utils.checks import is_staff, database_exists, ticket_parent


class Rename(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.slash_command(
        description=LocalizedDesc(english_us="To rename a ticket", french="Pour renommer un ticket"),
        dm_permission=False
    )
    @interactions.slash_option(
        name=LocalizedName(english_us="name", french="nom"),
        description=LocalizedDesc(english_us="New name for the ticket", french="Nouveau nom pour le ticket"),
        opt_type=interactions.OptionType.STRING,
        required=True
    )
    async def rename(self, ctx: interactions.SlashContext, name: str):
        if await database_exists(ctx) is not True:
            return

        if await is_staff(ctx) is not True:
            return

        if await ticket_parent(ctx) is not True:
            return

        await ctx.channel.edit(name=name)
        await ctx.send(f"Le ticket vient d'être renommé **{name}**.", ephemeral=True)


def setup(bot):
    Rename(bot)
