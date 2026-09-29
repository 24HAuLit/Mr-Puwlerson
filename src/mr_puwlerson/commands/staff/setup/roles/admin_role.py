import discord
from discord.ext import commands

from mr_puwlerson.commands.staff.setup._shared import handle_role_selection


class AdminRole(commands.Cog):
    @commands.Cog.listener("on_interaction")
    async def admin_role_choice(self, interaction: discord.Interaction):
        await handle_role_selection(
            interaction, "admin_menu", "Admin", "Admin", "mod_menu",
            "Quel role sera le role Modérateur ?\n*C'est à dire le role qui modérera le serveur.*",
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminRole())
