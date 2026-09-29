import discord
from discord.ext import commands

from mr_puwlerson.commands.staff.setup._shared import handle_role_selection


class DefaultRole(commands.Cog):
    @commands.Cog.listener("on_interaction")
    async def default_role_choice(self, interaction: discord.Interaction):
        await handle_role_selection(
            interaction, "default_menu", "Default", "par défaut", "staff_menu",
            "Quel role sera le role Staff ?\n*C'est a dire le role qui aura accès aux tickets, commande staff...*",
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(DefaultRole())
