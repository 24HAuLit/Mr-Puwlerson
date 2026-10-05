import sqlite3
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands


class ReloadExtension(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="reload_ext", description="Allows you to reload an extension.")
    @app_commands.describe(extension="Extension to reload")
    async def reload_ext(self, interaction: discord.Interaction, extension: str):
        if not await self.bot.is_owner(interaction.user):
            guild = interaction.guild
            path = Path(f"Database/{guild.id}.db") if guild is not None else None
            if path is None or not path.exists():
                message = (f"Database not found for ID `{guild.id}`. This server is not configured yet."
                           if guild is not None else ":x: You don't have the permission to do this.")
            else:
                with sqlite3.connect(path) as conn:
                    locale = conn.execute("SELECT locale FROM config").fetchone()[0]
                message = (":x: Vous n'avez pas la permission de faire ceci." if locale == "fr"
                           else ":x: You don't have the permission to do this.")
            await interaction.response.send_message(message, ephemeral=True)
            return

        try:
            await self.bot.reload_extension(extension)
        except commands.ExtensionError as error:
            await interaction.response.send_message(
                f"Cannot reload the extension **{extension}** : {error}", ephemeral=True
            )
        else:
            await interaction.response.send_message(f"Extension **{extension}** has been reloaded.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ReloadExtension(bot))
