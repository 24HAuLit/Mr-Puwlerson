import sqlite3
from contextlib import closing

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.staff.setup._shared import database_path, require_owner


class Locale(commands.Cog):
    @app_commands.command(name="locale", description="Change locale of the bot on the server.")
    @app_commands.describe(locale="The locale you want to set.")
    @app_commands.choices(locale=[
        app_commands.Choice(name="English", value="en"),
        app_commands.Choice(name="French", value="fr"),
    ])
    @app_commands.guild_only()
    async def locale(self, interaction: discord.Interaction, locale: str):
        if not await require_owner(interaction):
            return
        guild = interaction.guild
        if guild is None:
            return
        with closing(sqlite3.connect(database_path(guild.id))) as conn, conn:
            current = conn.execute("SELECT locale FROM config").fetchone()[0]
            if current != locale:
                conn.execute("UPDATE config SET locale = ?", (locale,))
        if locale == "fr":
            message = ("🇫🇷・La langue du bot est déjà en français." if current == locale else
                       "🇫🇷・La langue du bot a été changée en français.")
        else:
            message = ("🇬🇧・The bot's language is already in English." if current == locale else
                       "🇬🇧・The bot's language has been changed to English.")
        await interaction.response.send_message(message, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Locale())
