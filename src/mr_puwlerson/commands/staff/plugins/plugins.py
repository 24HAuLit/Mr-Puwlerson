import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.staff.banned_channel import (
    database_ready,
    has_permission,
    install_translator,
    localized,
)


class GiveawayChannelModal(discord.ui.Modal, title="Choix du salon"):
    def __init__(self):
        super().__init__(custom_id="giveaway_channel")

    giveaway_channel_text = discord.ui.TextInput(
        label="Veuillez entrer l'ID du salon", custom_id="giveaway_channel_text",
        min_length=1, max_length=100,
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None or not await database_ready(interaction) or not await has_permission(interaction, "owner_role"):
            return
        try:
            channel = guild.get_channel(int(self.giveaway_channel_text.value))
        except ValueError:
            channel = None
        if channel is None:
            await interaction.response.send_message("Veuillez entrer un ID de salon valable !", ephemeral=True)
            return

        with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
            old = conn.execute("SELECT id FROM channels WHERE lower(type) = 'giveaway'").fetchone()
            if old is not None and old[0] == channel.id:
                conn.execute("UPDATE plugins SET status = 'true' WHERE name = 'giveaway'")
                reply = f"Le salon `{channel.name}` est déjà le salon des giveaways !"
            else:
                if old is not None:
                    conn.execute("UPDATE channels SET type = NULL WHERE id = ?", (old[0],))
                exists = conn.execute("SELECT id FROM channels WHERE id = ?", (channel.id,)).fetchone()
                if exists is None:
                    conn.execute("INSERT INTO channels (name, id, type, hidden) VALUES (?, ?, 'giveaway', 0)",
                                 (channel.name, channel.id))
                else:
                    conn.execute("UPDATE channels SET type = 'giveaway' WHERE id = ?", (channel.id,))
                conn.execute("UPDATE plugins SET status = 'true' WHERE name = 'giveaway'")
                reply = (f"Le salon des giveaways a bien été changé pour `{channel.name}` !" if old
                         else "Le plugin `giveaway` a bien été activé !")
        await interaction.response.send_message(reply, ephemeral=True)


class Plugins(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="plugins", description=localized("Activate or deactivate plugins", "Active ou désactive des plugins"))
    @app_commands.guild_only()
    @app_commands.describe(plugin="Plugin a activer/désactiver", status="Status du plugin")
    @app_commands.choices(
        plugin=[
            app_commands.Choice(name="Suggestion", value="suggestion"),
            app_commands.Choice(name="Report", value="report"),
            app_commands.Choice(name="Giveaway", value="giveaway"),
        ],
        status=[
            app_commands.Choice(name="Activer", value="true"),
            app_commands.Choice(name="Désactiver", value="false"),
        ],
    )
    async def plugins(self, interaction: discord.Interaction, plugin: str, status: str):
        guild = interaction.guild
        if guild is None or not await database_ready(interaction) or not await has_permission(interaction, "owner_role"):
            return
        with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
            current = conn.execute("SELECT status FROM plugins WHERE name = ?", (plugin,)).fetchone()
            if current is not None and current[0] == status:
                await interaction.response.send_message(f"Le plugin `{plugin}` est déjà `{status}` !", ephemeral=True)
                return
            if plugin == "giveaway" and status == "true":
                await interaction.response.send_modal(GiveawayChannelModal())
                return
            conn.execute("UPDATE plugins SET status = ? WHERE name = ?", (status, plugin))
        message = (f"Le plugin `{plugin}` a bien été activé !" if status == "true"
                   else f"Le plugin `{plugin}` a bien été désactivé !")
        await interaction.response.send_message(message, ephemeral=True)


async def setup(bot: commands.Bot):
    await install_translator(bot)
    await bot.add_cog(Plugins(bot))
