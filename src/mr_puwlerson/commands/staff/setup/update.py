import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.staff.setup._shared import database_path


class Update(commands.Cog):
    @app_commands.command(name="update", description="Mise à jour de la base de données du serveur si nécessaire.")
    @app_commands.guild_only()
    async def update(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            return
        guild_id = guild.id
        if interaction.user.id != guild.owner_id:
            if not database_path(guild_id).exists():
                return await interaction.response.send_message(
                    f"Database not found for ID `{interaction.guild_id}`. This server is not configured yet.",
                    ephemeral=True,
                )
            conn = sqlite3.connect(database_path(guild_id))
            locale = conn.execute("SELECT locale FROM config").fetchone()[0]
            conn.close()
            message = (
                ":x: Vous n'avez pas la permission d'utiliser cette commande. Seul le propriétaire du serveur peut l'utiliser."
                if locale == "fr" else
                ":x: You don't have the permission to use this command. Only the server owner can use it."
            )
            return await interaction.response.send_message(message, ephemeral=True)

        if not database_path(guild_id).exists():
            return await interaction.response.send_message(
                f"Database not found for ID `{interaction.guild_id}`. This server is not configured yet.",
                ephemeral=True,
            )

        emoji = interaction.client.get_emoji(1083461392750878772)
        await interaction.response.send_message(
            f"{emoji if emoji else '🔄'}・Mise à jour de la base de données en cours...", ephemeral=True
        )

        table_name = ["locale", "plugins", "roles", "channels", "ticket", "ticket_count", "logs_channels", "blacklist"]

        conn = sqlite3.connect(database_path(guild_id))
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS locale (locale TEXT DEFAULT 'en')")
        c.execute("CREATE TABLE IF NOT EXISTS plugins (name TEXT, status TEXT default false)")
        c.execute("CREATE TABLE IF NOT EXISTS roles (name TEXT, id INTEGER, type TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS channels (name TEXT, id INTEGER, type TEXT, hidden INTEGER default 0)")
        c.execute("CREATE TABLE IF NOT EXISTS ticket (ticket_id INTEGER PRIMARY KEY autoincrement, author_id INTEGER, "
                  "staff_id INTEGER, channel_id INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS ticket_count (user_id INTEGER, count INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS logs_channels (name TEXT, id INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS blacklist (blacklist_id INTEGER PRIMARY KEY autoincrement, "
                  "user_id INTEGER, reason TEXT)")

        conn.commit()

        for table in table_name:
            columns = [col[1] for col in c.execute(f"PRAGMA table_info({table})").fetchall()]

            if table == "locale":
                if "locale" not in columns:
                    c.execute("ALTER TABLE locale ADD COLUMN locale TEXT DEFAULT 'en'")
                    conn.commit()
            elif table == "plugins":
                if "name" not in columns:
                    c.execute("ALTER TABLE plugins ADD COLUMN name TEXT")
                    conn.commit()
                if "status" not in columns:
                    c.execute("ALTER TABLE plugins ADD COLUMN status TEXT default false")
                    conn.commit()
            elif table == "roles":
                if "name" not in columns:
                    c.execute("ALTER TABLE roles ADD COLUMN name TEXT")
                    conn.commit()
                if "id" not in columns:
                    c.execute("ALTER TABLE roles ADD COLUMN id INTEGER")
                    conn.commit()
                if "type" not in columns:
                    c.execute("ALTER TABLE roles ADD COLUMN type TEXT")
                    conn.commit()
            elif table == "channels":
                if "name" not in columns:
                    c.execute("ALTER TABLE channels ADD COLUMN name TEXT")
                    conn.commit()
                if "id" not in columns:
                    c.execute("ALTER TABLE channels ADD COLUMN id INTEGER")
                    conn.commit()
                if "type" not in columns:
                    c.execute("ALTER TABLE channels ADD COLUMN type TEXT")
                    conn.commit()
                if "hidden" not in columns:
                    c.execute("ALTER TABLE channels ADD COLUMN hidden INTEGER default 0")
                    conn.commit()
            elif table == "ticket":
                if "ticket_id" not in columns:
                    c.execute("ALTER TABLE ticket ADD COLUMN ticket_id INTEGER PRIMARY KEY autoincrement")
                    conn.commit()
                if "author_id" not in columns:
                    c.execute("ALTER TABLE ticket ADD COLUMN author_id INTEGER")
                    conn.commit()
                if "staff_id" not in columns:
                    c.execute("ALTER TABLE ticket ADD COLUMN staff_id INTEGER")
                    conn.commit()
                if "channel_id" not in columns:
                    c.execute("ALTER TABLE ticket ADD COLUMN channel_id INTEGER")
                    conn.commit()
            elif table == "ticket_count":
                if "user_id" not in columns:
                    c.execute("ALTER TABLE ticket_count ADD COLUMN user_id INTEGER")
                    conn.commit()
                if "count" not in columns:
                    c.execute("ALTER TABLE ticket_count ADD COLUMN count INTEGER")
                    conn.commit()
            elif table == "logs_channels":
                if "name" not in columns:
                    c.execute("ALTER TABLE logs_channels ADD COLUMN name TEXT")
                    conn.commit()
                if "id" not in columns:
                    c.execute("ALTER TABLE logs_channels ADD COLUMN id INTEGER")
                    conn.commit()
            elif table == "blacklist":
                if "blacklist_id" not in columns:
                    c.execute("ALTER TABLE blacklist ADD COLUMN blacklist_id INTEGER PRIMARY KEY autoincrement")
                    conn.commit()
                if "user_id" not in columns:
                    c.execute("ALTER TABLE blacklist ADD COLUMN user_id INTEGER")
                    conn.commit()
                if "reason" not in columns:
                    c.execute("ALTER TABLE blacklist ADD COLUMN reason TEXT")
                    conn.commit()

        conn.close()

        await interaction.followup.send("✅・Mise à jour de la base de données terminée !", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Update())
