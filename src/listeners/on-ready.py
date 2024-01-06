from interactions import Extension, Client, listen
from datetime import datetime


class OnReady(Extension):
    def __init__(self, bot):
        self.bot: Client = bot

    @listen()
    async def on_ready(self):
        print("+------------------+")
        print(f"Logged in as {self.bot.user.username} (ID : {self.bot.user.id})")
        print(f"Connected to {len(self.bot.guilds)} guilds")
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        print("+------------------+")

        self.bot.load_extension("src.listeners.on_guild_join")
