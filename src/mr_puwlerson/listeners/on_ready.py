from datetime import datetime

from discord.ext import commands


class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('+------------------+')
        print(f'Logged in as {self.bot.user} (ID : {self.bot.user.id})')
        print(f'Connected to {len(self.bot.guilds)} guilds')
        print(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))  # noqa: DTZ005
        print('+------------------+')


async def setup(bot):
    await bot.add_cog(OnReady(bot))
    # Load the guild-initialization listener once, not on every reconnect.
    if 'mr_puwlerson.listeners.on_guild_join' not in bot.extensions:
        await bot.load_extension('mr_puwlerson.listeners.on_guild_join')
