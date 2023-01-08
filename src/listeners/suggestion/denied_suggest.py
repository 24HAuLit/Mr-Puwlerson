import interactions
from src.listeners.suggestion.components.deny import modal_deny


class SuggestionDenied(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("refuse")
    async def button_refuse(self, ctx):
        if interactions.Permissions.ADMINISTRATOR not in ctx.author.permissions:
            await ctx.send("Vous n'avez pas la permission de refuser une suggestion.", ephemeral=True)
        else:
            await ctx.popup(modal_deny())


def setup(bot):
    SuggestionDenied(bot)
