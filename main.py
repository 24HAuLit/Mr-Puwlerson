import interactions
from interactions.ext.voice import VoiceClient
from interactions.ext.wait_for import setup
from dotenv import load_dotenv

load_dotenv()

from const import *


class Main:
    def __init__(self):
        self.bot = interactions.Client(token=TOKEN, intents=interactions.Intents.ALL)

        interactions.ext.wait_for.setup(self.bot)
        self.setup()

        self.bot.start()

    def setup(self):
        # Partie commandes
        [self.bot.load(f"src.commands.{ext}") for ext in COMMANDS]
        [self.bot.load(f"src.commands.staff.{ext}") for ext in COMMANDS_STAFF]
        [self.bot.load(f"src.commands.ticket.{ext}") for ext in COMMANDS_TICKET]

        # Partie listeners
        [self.bot.load(f"src.listeners.{ext}") for ext in LISTENERS]
        [self.bot.load(f"src.listeners.logs.{ext}") for ext in LISTENERS_LOGS]
        [self.bot.load(f"src.listeners.report.{ext}") for ext in LISTENERS_REPORT]
        [self.bot.load(f"src.listeners.suggestion.{ext}") for ext in LISTENERS_SUGGEST]
        [self.bot.load(f"src.listeners.ticket.{ext}") for ext in LISTENERS_TICKET]


if __name__ == '__main__':
    Main()
