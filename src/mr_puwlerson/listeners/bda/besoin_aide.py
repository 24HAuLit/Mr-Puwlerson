import discord
from discord.ext import commands


class BesoinAide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        # The original listener's voice-channel creation logic was disabled.
        pass


async def setup(bot):
    await bot.add_cog(BesoinAide(bot))
