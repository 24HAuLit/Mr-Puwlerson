import discord
from discord.ext import commands

from mr_puwlerson.commands.staff.setup._shared import handle_role_selection


class StaffRole(commands.Cog):
    @commands.Cog.listener("on_interaction")
    async def staff_role_choice(self, interaction: discord.Interaction):
        await handle_role_selection(
            interaction, "staff_menu", "Staff", "Staff", "owner_menu",
            "Quel role sera le role Owner ?\n*C'est à dire le role du créateur du serveur*",
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(StaffRole())
