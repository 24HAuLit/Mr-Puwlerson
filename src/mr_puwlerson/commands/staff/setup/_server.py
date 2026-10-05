"""Server-type selector and log-server setup for /setup server."""

import sqlite3
from contextlib import closing

import discord
from discord.ext import commands

from mr_puwlerson.commands.staff.setup._shared import database_path, require_owner
from mr_puwlerson.database import initialize_database

LOG_CHANNELS = {
    "messages": ("new", "edit", "delete"),
    "moderation": ("clear", "timeout", "ban", "blacklist", "nuke"),
    "tickets": ("create", "close"),
    "serveur": ("join-quit", "report", "giveaway"),
}


class MainServerModal(discord.ui.Modal, title="Serveur de logs"):
    main_server_id = discord.ui.TextInput(
        label="ID du serveur principal", custom_id="text_input_main_server_id",
        min_length=17, max_length=20,
    )

    def __init__(self, bot: commands.Bot):
        super().__init__(custom_id="main_server_id")
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        if not await require_owner(interaction):
            return
        logs_guild = interaction.guild
        try:
            main_id = int(self.main_server_id.value)
        except ValueError:
            await interaction.response.send_message("ID du serveur principal invalide.", ephemeral=True)
            return
        main_guild = self.bot.get_guild(main_id)
        if (logs_guild is None or main_guild is None or main_guild.id == logs_guild.id
                or main_guild.owner_id != interaction.user.id or not database_path(main_id).exists()):
            await interaction.response.send_message(
                "Le serveur principal doit déjà être configuré, appartenir au propriétaire du serveur de logs "
                "et être différent de ce serveur.", ephemeral=True,
            )
            return
        await interaction.response.defer(ephemeral=True)
        try:
            initialize_database(main_id)
            overwrites: dict[discord.Role | discord.Member | discord.Object, discord.PermissionOverwrite] = {
                logs_guild.default_role: discord.PermissionOverwrite(view_channel=False)
            }
            if logs_guild.me is not None:
                overwrites[logs_guild.me] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
            mappings = {}
            for category_name, channel_names in LOG_CHANNELS.items():
                category = discord.utils.get(logs_guild.categories, name=category_name)
                if category is None:
                    category = await logs_guild.create_category(category_name, overwrites=overwrites)
                for channel_name in channel_names:
                    channel = discord.utils.get(category.text_channels, name=channel_name)
                    if channel is None:
                        channel = await logs_guild.create_text_channel(
                            channel_name, category=category, overwrites=category.overwrites,
                        )
                    mappings[channel_name] = channel.id
            with closing(sqlite3.connect(database_path(main_id))) as conn, conn:
                conn.execute("UPDATE config SET logs_server = ?", (logs_guild.id,))
                for name, channel_id in mappings.items():
                    if conn.execute("SELECT 1 FROM logs_channels WHERE name = ?", (name,)).fetchone():
                        conn.execute("UPDATE logs_channels SET id = ? WHERE name = ?", (channel_id, name))
                    else:
                        conn.execute("INSERT INTO logs_channels (name, id) VALUES (?, ?)", (name, channel_id))
        except (discord.HTTPException, sqlite3.Error, ValueError) as error:
            await interaction.followup.send(f"Configuration du serveur de logs impossible : {error}", ephemeral=True)
            return
        await interaction.followup.send("Configuration du serveur de logs terminée.", ephemeral=True)


class ServerTypeSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            custom_id="server_type", placeholder="Quel type de serveur voulez-vous configurer ?",
            options=[
                discord.SelectOption(label="Serveur principal", value="main"),
                discord.SelectOption(label="Serveur de logs", value="logs"),
            ],
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        if not await require_owner(interaction):
            return
        if self.values[0] == "main":
            guild = interaction.guild
            if guild is None:
                return
            initialize_database(guild.id)
            await interaction.response.send_message(
                "Configuration du serveur principal terminée. Vous pouvez désormais configurer les channels "
                "et les roles.", ephemeral=True,
            )
        else:
            await interaction.response.send_modal(MainServerModal(self.bot))
