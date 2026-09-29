import sqlite3

import discord
from discord.ext import commands

from mr_puwlerson.listeners import database_path, has_role, view
from mr_puwlerson.listeners.ticket.components.close import (
    ticket_close,
    ticket_close_reason,
)


class ClaimTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component or interaction.data is None or interaction.data.get('custom_id') != 'claim_ticket':
            return
        if interaction.guild_id is None or not isinstance(interaction.user, discord.Member):
            return
        if not database_path(interaction.guild_id).exists() or not has_role(interaction.user, 'staff_role'):
            return await interaction.response.send_message('Permissions insuffisantes.', ephemeral=True)
        with sqlite3.connect(database_path(interaction.guild_id)) as conn:
            conn.execute('UPDATE ticket SET staff_id = ? WHERE channel_id = ?', (interaction.user.id, interaction.channel_id))
        await interaction.response.edit_message(view=view(ticket_close(), ticket_close_reason()))
        await interaction.followup.send(embed=discord.Embed(description=f'Le ticket a été pris en charge par {interaction.user.mention}.', color=0x2ECC70))


async def setup(bot):
    await bot.add_cog(ClaimTicket(bot))
