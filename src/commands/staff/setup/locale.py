import sqlite3
import interactions
from message_config import ErrorMessage
from os.path import exists


class Locale(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    @interactions.option(
        name="locale",
        description="The locale you want to set.",
        type=interactions.OptionType.STRING,
        required=True,
        choices=[
            interactions.Choice(name="English", value="en"),
            interactions.Choice(name="French", value="fr")
        ]
    )
    async def locale(self, ctx: interactions.CommandContext, locale: str):
        """Change locale of the bot on the server."""
        if ctx.author.id == ctx.guild.owner_id:
            if exists("./Database/{}.db".format(ctx.guild_id)) is False:
                return await ctx.send(ErrorMessage.database_not_found(ctx.guild_id), ephemeral=True)
            else:
                conn = sqlite3.connect(f'./Database/{ctx.guild_id}.db')
                c = conn.cursor()
                c.execute("SELECT locale FROM locale")
                if locale == 'fr':
                    if locale == c.fetchone()[0]:
                        conn.close()
                        return await ctx.send("🇫🇷・La langue du bot est déjà en français.", ephemeral=True)
                    else:
                        c.execute("UPDATE locale SET locale = 'fr'")
                        conn.commit()
                        conn.close()
                        return await ctx.send("🇫🇷・La langue du bot a été changée en français.", ephemeral=True)
                elif locale == 'en':
                    if locale == c.fetchone()[0]:
                        conn.close()
                        return await ctx.send("🇬🇧・The bot's language is already in English.", ephemeral=True)
                    else:
                        c.execute("UPDATE locale SET locale = 'en'")
                        conn.commit()
                        conn.close()
                        return await ctx.send("🇬🇧・The bot's language has been changed to English.", ephemeral=True)
        else:
            return await ctx.send(ErrorMessage.OwnerOnly(), ephemeral=True)


def setup(bot):
    Locale(bot)
