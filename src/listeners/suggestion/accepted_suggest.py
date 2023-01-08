import interactions
from src.listeners.suggestion.components.accept import modal_accept


class SuggestionAccepted(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("accept")
    async def button_accept(self, ctx):
        if interactions.Permissions.ADMINISTRATOR not in ctx.author.permissions:
            await ctx.send("Vous n'avez pas la permission d'accepter une suggestion.", ephemeral=True)
        else:
            await ctx.popup(modal_accept())


def setup(bot):
    SuggestionAccepted(bot)
