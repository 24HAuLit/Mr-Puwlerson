import discord
from discord.ext import commands

from mr_puwlerson.listeners import database_path, has_role
from mr_puwlerson.listeners.ticket.confirm_close import close_ticket


class CloseReason(discord.ui.Modal, title='Raison'):
    reason = discord.ui.TextInput(label='Raison', placeholder='Raison de la fermeture du ticket', custom_id='short_response', style=discord.TextStyle.paragraph, min_length=1, max_length=512)

    def __init__(self, bot):
        super().__init__(custom_id="close_reason")
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await close_ticket(self.bot, interaction, str(self.reason))


class CloseReasonTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component or interaction.data is None or interaction.data.get('custom_id') != 'close_reason_ticket':
            return
        if interaction.guild_id is None or not isinstance(interaction.user, discord.Member):
            return
        if not database_path(interaction.guild_id).exists() or not has_role(interaction.user, 'staff_role'):
            return await interaction.response.send_message('Permissions insuffisantes.', ephemeral=True)
        await interaction.response.send_modal(CloseReason(self.bot))


async def setup(bot):
    await bot.add_cog(CloseReasonTicket(bot))
