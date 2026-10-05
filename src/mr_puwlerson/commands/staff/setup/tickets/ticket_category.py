import sqlite3
from contextlib import closing

import discord
from discord.ext import commands

from mr_puwlerson.commands.staff.setup._shared import database_path, require_owner


class TicketCategory(commands.Cog):
    @commands.Cog.listener("on_interaction")
    async def ticket_category(self, interaction: discord.Interaction):
        if (interaction.type != discord.InteractionType.component or not interaction.data
                or interaction.data.get("custom_id") != "ticket_category"):
            return
        guild = interaction.guild
        if guild is None or not interaction.data.get("values"):
            return
        if not await require_owner(interaction):
            return
        values = interaction.data.get("values")
        if not values:
            return
        channel_id = int(values[0])
        channel = guild.get_channel(channel_id)
        if not isinstance(channel, discord.CategoryChannel):
            await interaction.response.send_message("Cette catégorie n'existe plus.", ephemeral=True)
            return
        with closing(sqlite3.connect(database_path(guild.id))) as conn, conn:
            row = conn.execute("SELECT name, id FROM channels WHERE type = 'ticket_parent'").fetchone()
            if row is not None and row[1] == channel_id:
                message = f"**{channel.name}** est déjà la catégorie pour les tickets"
            else:
                if row is not None:
                    conn.execute("UPDATE channels SET type = NULL WHERE id = ?", (row[1],))
                if conn.execute("SELECT 1 FROM channels WHERE id = ?", (channel_id,)).fetchone():
                    conn.execute("UPDATE channels SET type = 'ticket_parent' WHERE id = ?", (channel_id,))
                else:
                    conn.execute("INSERT INTO channels (name, id, type) VALUES (?, ?, 'ticket_parent')",
                                 (channel.name, channel_id))
                message = (f"**{row[0]}** n'est plus la catégorie pour les tickets, elle a été remplacée "
                           f"par **{channel.name}**" if row else
                           f"**{channel.name}** est désormais la catégorie de tickets")
            conn.execute("UPDATE config SET ticket_parent = ?", (channel_id,))
        await interaction.response.send_message(message, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCategory())
