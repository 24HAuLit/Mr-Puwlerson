import discord
from discord.ext import commands

from mr_puwlerson.database import initialize_database


class OnNewGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # on_guild_join is not emitted for guilds the bot was already in at startup.
        for guild in self.bot.guilds:
            initialize_database(guild.id)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        initialize_database(guild.id)


async def setup(bot):
    await bot.add_cog(OnNewGuild(bot))
