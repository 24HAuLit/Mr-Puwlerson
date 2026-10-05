from datetime import UTC, datetime

import discord
from discord.ext import commands

from mr_puwlerson.listeners import database_path, has_role
from mr_puwlerson.listeners.suggestion.components.deny import modal_deny
from mr_puwlerson.utils.const import DATA


class SuggestionDenied(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component or interaction.data is None or interaction.data.get('custom_id') != 'refuse':
            return
        if interaction.guild_id is None or not isinstance(interaction.user, discord.Member):
            return
        if not database_path(interaction.guild_id).exists() or not has_role(interaction.user, 'admin_role'):
            return await interaction.response.send_message('Permissions insuffisantes.', ephemeral=True)

        original = interaction.message
        if original is None:
            return await interaction.response.send_message("Suggestion introuvable.", ephemeral=True)

        async def submit(modal_interaction):
            source = original.embeds[0]
            result = self.bot.get_channel(DATA['main']['suggest_result'])
            embed = discord.Embed(title='Suggestion refusé', url=original.jump_url, color=0xFF3C3C, timestamp=datetime.now(UTC))
            embed.add_field(name='__**Suggestion : **__', value=source.description, inline=False)
            embed.add_field(name='__**Raison : **__', value=str(modal.reason), inline=False)
            embed.set_footer(icon_url=modal_interaction.user.display_avatar.url, text=f'Suggestion refusé par {modal_interaction.user}.')
            updated = discord.Embed(title=source.title, description=source.description, color=0xFF3C3C, timestamp=source.timestamp)
            updated.set_footer(icon_url=source.footer.icon_url, text=source.footer.text)
            await original.edit(embed=updated, view=None)
            await modal_interaction.response.send_message('Vous avez refusé cette suggestion.', ephemeral=True)
            await result.send(embed=embed)

        modal = modal_deny(submit)
        await interaction.response.send_modal(modal)


async def setup(bot):
    await bot.add_cog(SuggestionDenied(bot))
