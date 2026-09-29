import discord
from discord.ext import commands

from mr_puwlerson.commands.staff.setup._shared import handle_role_selection


class ModRole(commands.Cog):
    @commands.Cog.listener("on_interaction")
    async def mod_role_choice(self, interaction: discord.Interaction):
        await handle_role_selection(interaction, "mod_menu", "Mod", "Modérateur")


async def setup(bot: commands.Bot):
    await bot.add_cog(ModRole())
