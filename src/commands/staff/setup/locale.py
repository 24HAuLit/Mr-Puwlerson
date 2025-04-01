import sqlite3
import interactions
from src.utils.checks import database_exists, is_owner
from src.utils.message_config import ErrorMessage


class Locale(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.slash_command()
    @interactions.slash_option(
        name="locale",
        description="The locale you want to set.",
        opt_type=3,
        required=True,
        choices=[
            interactions.SlashCommandChoice(name="English", value="en"),
            interactions.SlashCommandChoice(name="French", value="fr")
        ]
    )
    async def locale(self, ctx: interactions.SlashContext, locale: str):
        """Change locale of the bot on the server."""
        if not await database_exists(ctx):
            return

        if not await is_owner(ctx):
            return await ctx.send(ErrorMessage.MissingPermissions(ctx.guild.id), ephemeral=True)

        conn = sqlite3.connect(f'./Database/{ctx.guild.id}.db')
        c = conn.cursor()
        c.execute("SELECT locale FROM config")
        if locale == 'fr':
            if locale == c.fetchone()[0]:
                conn.close()
                return await ctx.send("🇫🇷・La langue du bot est déjà en français.", ephemeral=True)
            else:
                c.execute("UPDATE config SET locale = 'fr'")
                conn.commit()
                conn.close()
                return await ctx.send("🇫🇷・La langue du bot a été changée en français.", ephemeral=True)
        elif locale == 'en':
            if locale == c.fetchone()[0]:
                conn.close()
                return await ctx.send("🇬🇧・The bot's language is already in English.", ephemeral=True)
            else:
                c.execute("UPDATE config SET locale = 'en'")
                conn.commit()
                conn.close()
                return await ctx.send("🇬🇧・The bot's language has been changed to English.", ephemeral=True)


def setup(bot):
    Locale(bot)
