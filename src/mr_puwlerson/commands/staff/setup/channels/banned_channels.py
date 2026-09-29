import sqlite3
from contextlib import closing

import discord
from discord.ext import commands

from mr_puwlerson.commands.staff.setup._shared import database_path


class SetupBannedChannels(commands.Cog):
    @commands.Cog.listener("on_interaction")
    async def select(self, interaction: discord.Interaction):
        if (interaction.type != discord.InteractionType.component or not interaction.data
                or interaction.data.get("custom_id") != "banned_channels"):
            return
        guild = interaction.guild
        if guild is None:
            return
        messages = []
        with closing(sqlite3.connect(database_path(guild.id))) as conn, conn:
            for value in interaction.data.get("values", []):
                channel_id = int(value)
                channel = guild.get_channel(channel_id)
                if channel is None:
                    continue
                row = conn.execute("SELECT hidden FROM channels WHERE id = ?", (channel_id,)).fetchone()
                if row is None:
                    conn.execute("INSERT INTO channels (name, id, type, hidden) VALUES (?, ?, NULL, 1)",
                                 (channel.name, channel_id))
                    hidden = 1
                else:
                    hidden = 0 if row[0] == 1 else 1
                    conn.execute("UPDATE channels SET hidden = ? WHERE id = ?", (hidden, channel_id))
                if hidden:
                    messages.append(f"**{channel.name}** est désormais un channel 'banni' des logs")
                else:
                    messages.append(f"**{channel.name}** n'est plus un channel 'banni' des logs")
        if messages:
            await interaction.response.send_message(messages[0], ephemeral=True)
            for message in messages[1:]:
                await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message("Aucun salon valide sélectionné.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(SetupBannedChannels())
