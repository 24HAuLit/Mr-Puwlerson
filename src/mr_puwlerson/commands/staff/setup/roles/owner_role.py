import discord
from discord.ext import commands

from mr_puwlerson.commands.staff.setup._shared import handle_role_selection


class OwnerRole(commands.Cog):
    @commands.Cog.listener("on_interaction")
    async def owner_role_choice(self, interaction: discord.Interaction):
        await handle_role_selection(
            interaction, "owner_menu", "Owner", "Owner", "admin_menu",
            "Quel role sera le role Admin ?\n*C'est à dire le role qui sera la pour assister le role Owner*",
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(OwnerRole())
