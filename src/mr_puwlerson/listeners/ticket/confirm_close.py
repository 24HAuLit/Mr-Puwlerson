import asyncio
import sqlite3
from datetime import UTC, datetime

import discord
from discord.ext import commands

from mr_puwlerson.listeners import database_path, has_role


async def close_ticket(bot, interaction: discord.Interaction, reason: str):
    channel = interaction.channel
    guild = interaction.guild
    if guild is None or not isinstance(channel, discord.TextChannel):
        return await interaction.response.send_message('Ticket introuvable.', ephemeral=True)
    with sqlite3.connect(database_path(guild.id)) as conn:
        row = conn.execute('SELECT * FROM ticket WHERE channel_id = ?', (channel.id,)).fetchone()
        if row is None:
            return await interaction.response.send_message('Ticket introuvable.', ephemeral=True)
        conn.execute('UPDATE ticket_count SET count = count - 1 WHERE user_id = ?', (row[1],))
        log_id = conn.execute("SELECT id FROM logs_channels WHERE name = 'close'").fetchone()[0]

    await interaction.response.send_message(embed=discord.Embed(description='**Transcript HS** pour une durée indéterminée.', color=0xFF0000))
    await interaction.followup.send(embed=discord.Embed(description='Ce ticket va être fermé dans quelques instant...', color=0xFF0000))
    await asyncio.sleep(5)
    await channel.delete()

    embed = discord.Embed(title='Fermeture de ticket', description='Un ticket a été fermé.', color=0xFF4646, timestamp=datetime.now(UTC))
    embed.add_field(name='__**Ticket ID**__', value=str(row[0]))
    embed.add_field(name='__**Ouvert par**__', value=f'<@{row[1]}>')
    embed.add_field(name='__**Fermé par**__', value=interaction.user.mention)

    if row[2] is not None and row[2] != 'None':
        embed.add_field(name='__**Claim par**__', value=f'<@{row[2]}>')
    embed.add_field(name='__**Raison**__', value=reason)
    logs = bot.get_channel(log_id)
    await logs.send(embed=embed)


class ConfirmClose(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component or interaction.data is None or interaction.data.get('custom_id') != 'confirm_close':
            return
        if interaction.guild_id is None or not isinstance(interaction.user, discord.Member):
            return
        if not database_path(interaction.guild_id).exists() or not has_role(interaction.user, 'staff_role'):
            return await interaction.response.send_message('Permissions insuffisantes.', ephemeral=True)
        await close_ticket(self.bot, interaction, 'Aucune raison fournie')


async def setup(bot):
    await bot.add_cog(ConfirmClose(bot))
