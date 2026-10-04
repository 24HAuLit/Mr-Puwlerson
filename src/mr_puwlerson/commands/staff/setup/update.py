import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.staff.setup._shared import database_path
from mr_puwlerson.database import initialize_database


class Update(commands.Cog):
    @app_commands.command(name="update", description="Mise à jour de la base de données du serveur si nécessaire.")
    @app_commands.guild_only()
    async def update(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            return
        if interaction.user.id != guild.owner_id:
            if not database_path(guild.id).exists():
                return await interaction.response.send_message(
                    f"Database not found for ID `{guild.id}`. This server is not configured yet.",
                    ephemeral=True,
                )
            with sqlite3.connect(database_path(guild.id)) as conn:
                row = conn.execute("SELECT locale FROM config").fetchone()
            locale = row[0] if row is not None else "en"
            message = (
                ":x: Vous n'avez pas la permission d'utiliser cette commande. Seul le propriétaire du serveur peut l'utiliser."
                if locale == "fr" else
                ":x: You don't have the permission to use this command. Only the server owner can use it."
            )
            return await interaction.response.send_message(message, ephemeral=True)

        emoji = interaction.client.get_emoji(1083461392750878772)
        await interaction.response.send_message(
            f"{emoji if emoji else '🔄'}・Mise à jour de la base de données en cours...", ephemeral=True
        )
        try:
            initialize_database(guild.id)
        except (ValueError, sqlite3.Error) as error:
            await interaction.followup.send(f"Mise à jour de la base de données impossible : {error}", ephemeral=True)
            return
        await interaction.followup.send("✅・Mise à jour de la base de données terminée !", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Update())
