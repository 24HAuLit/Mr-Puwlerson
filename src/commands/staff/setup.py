import interactions
from interactions.ext.checks import is_owner


class Setup(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.select_menu = interactions.SelectMenu(
            custom_id="select",
            options=[
                interactions.SelectOption(label="Serveur principal", value="main"),
                interactions.SelectOption(label="Serveur de logs", value="logs")
            ]
        )

    @interactions.extension_command()
    async def setup(self, ctx: interactions.CommandContext):
        await ctx.send("Quel type de serveur voulez-vous configurer ?", components=self.select_menu, ephemeral=True)

    @interactions.extension_component("select")
    async def select(self, ctx: interactions.CommandContext, choice: list[str]):
        if choice[0] == "main":
            await ctx.send("main test", ephemeral=True)
        else:
            await ctx.send("logs test", ephemeral=True)


def setup(bot):
    Setup(bot)
