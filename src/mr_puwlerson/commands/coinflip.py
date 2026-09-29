from random import choice

import discord
from discord import app_commands
from discord.ext import commands


class FrenchCommandTranslator(app_commands.Translator):
    def __init__(self, previous: app_commands.Translator | None = None):
        self.previous = previous

    async def translate(self, string: app_commands.locale_str, locale: discord.Locale,
                        context: app_commands.TranslationContext) -> str | None:
        if locale == discord.Locale.french and "fr" in string.extras:
            return string.extras["fr"]
        if self.previous is not None:
            return await self.previous.translate(string, locale, context)
        return None


async def enable_french_localizations(bot: commands.Bot):
    if not isinstance(bot.tree.translator, FrenchCommandTranslator):
        await bot.tree.set_translator(FrenchCommandTranslator(bot.tree.translator))


class PileFace(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name=app_commands.locale_str("coinflip", fr="pileface"),
        description=app_commands.locale_str("Flip a coin and show the result", fr="Lance une pièce et affiche le résultat"),
    )
    async def coinflip(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"La pièce est tombé sur **{choice(['pile', 'face'])}**")


async def setup(bot: commands.Bot):
    await enable_french_localizations(bot)
    await bot.add_cog(PileFace(bot))
