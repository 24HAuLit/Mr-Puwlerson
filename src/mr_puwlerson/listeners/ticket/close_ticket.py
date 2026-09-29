import discord
from discord.ext import commands

from mr_puwlerson.listeners import database_path, has_role, view
from mr_puwlerson.listeners.ticket.components.close import confirm_close


class CloseTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component or interaction.data is None or interaction.data.get('custom_id') != 'close_ticket':
            return
        if interaction.guild_id is None or not isinstance(interaction.user, discord.Member):
            return
        if not database_path(interaction.guild_id).exists() or not has_role(interaction.user, 'staff_role'):
            return await interaction.response.send_message('Permissions insuffisantes.', ephemeral=True)
        await interaction.response.send_message('Êtes-vous sur de vouloir fermer ce ticket ?', view=view(confirm_close()), ephemeral=True)


async def setup(bot):
    await bot.add_cog(CloseTicket(bot))
