import interactions


class OnReady(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_listener()
    async def on_ready(self):
        print("+------------------+")
        print(f"Logged in as {self.bot.me.name} (ID : {self.bot.me.id})")
        print(f"Connected to {len(self.bot.guilds)} guilds")
        print("+------------------+")


def setup(bot):
    OnReady(bot)
