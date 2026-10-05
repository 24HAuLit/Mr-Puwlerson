"""Checks and component helpers for the setup extensions."""

import sqlite3
from contextlib import closing
from pathlib import Path

import discord


def database_path(guild_id: int) -> Path:
    return Path("Database") / f"{guild_id}.db"


async def require_owner(interaction: discord.Interaction) -> bool:
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return False
    if not database_path(guild.id).exists():
        await interaction.response.send_message(
            f"Database not found for ID `{guild.id}`. This server is not configured yet.", ephemeral=True
        )
        return False
    with closing(sqlite3.connect(database_path(guild.id))) as conn:
        owner_role = conn.execute("SELECT owner_role FROM config").fetchone()[0]
        locale = conn.execute("SELECT locale FROM config").fetchone()[0]
    if interaction.user.id == guild.owner_id or any(
        role.id == owner_role for role in getattr(interaction.user, "roles", ())
    ):
        return True
    message = (
        ":x: Vous n'avez pas la permission de faire ceci."
        if locale == "fr" else ":x: You don't have the permission to do this."
    )
    await interaction.response.send_message(message, ephemeral=True)
    return False


async def handle_role_selection(
    interaction: discord.Interaction, custom_id: str, role_type: str,
    description: str, next_menu: str | None = None, next_prompt: str | None = None,
) -> None:
    if (interaction.type != discord.InteractionType.component
            or not interaction.data or interaction.data.get("custom_id") != custom_id):
        return
    guild = interaction.guild
    if guild is None or not interaction.data.get("values"):
        return
    if not await require_owner(interaction):
        return
    values = interaction.data.get("values")
    if not values:
        return
    role = guild.get_role(int(values[0]))
    if role is None:
        await interaction.response.send_message("Ce rôle n'existe plus.", ephemeral=True)
        return

    with closing(sqlite3.connect(database_path(guild.id))) as conn, conn:
        row = conn.execute("SELECT name, id FROM roles WHERE type = ?", (role_type,)).fetchone()
        if row is not None and row[1] == role.id:
            message = f"**{role.name}** est déjà le role {description}."
        else:
            if row is not None:
                conn.execute("UPDATE roles SET type = NULL WHERE id = ?", (row[1],))
            # Role-create events normally populate this table; handle a missing row as well.
            if conn.execute("SELECT 1 FROM roles WHERE id = ?", (role.id,)).fetchone():
                conn.execute("UPDATE roles SET type = ? WHERE id = ?", (role_type, role.id))
            else:
                conn.execute("INSERT INTO roles (name, id, type) VALUES (?, ?, ?)",
                             (role.name, role.id, role_type))
            message = (f"**{row[0]}** n'est plus le role {description}, il a été remplacé "
                       f"par **{role.name}**." if row else
                       f"**{role.name}** est désormais le role {description}.")
        column = {"Default": "default_role", "Staff": "staff_role", "Owner": "owner_role",
                  "Admin": "admin_role"}.get(role_type)
        if column is not None:
            conn.execute(f"UPDATE config SET {column} = ?", (role.id,))

    await interaction.response.send_message(message, ephemeral=True)
    if next_menu is not None and next_prompt is not None:
        view = discord.ui.View()
        view.add_item(discord.ui.RoleSelect(custom_id=next_menu, placeholder="Choisissez un rôle"))
        await interaction.followup.send(next_prompt, view=view, ephemeral=True)
    else:
        await interaction.followup.send(
            "La configuration des roles est terminée, vous pouvez donc passer à la suite des "
            "configurations ou utiliser le bot", ephemeral=True
        )
