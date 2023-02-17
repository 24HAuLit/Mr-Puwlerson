import interactions
from dotenv import load_dotenv

load_dotenv()

from const import *


class Main:
    def __init__(self):
        self.bot = interactions.Client(token=TOKEN, intents=interactions.Intents.ALL)
        self.setup()
        self.bot.start()

    def setup(self):
        # Partie commandes
        [self.bot.load(f"src.commands.{ext}") for ext in COMMANDS]
        [self.bot.load(f"src.commands.staff.{ext}") for ext in COMMANDS_STAFF]
        [self.bot.load(f"src.commands.ticket.{ext}") for ext in COMMANDS_TICKET]
        [self.bot.load(f"src.commands.staff.setup.{ext}") for ext in COMMANDS_SETUP]
        [self.bot.load(f"src.commands.staff.setup.roles.{ext}") for ext in SETUP_ROLES]
        [self.bot.load(f"src.commands.staff.setup.channels.{ext}") for ext in SETUP_CHANNELS]
        [self.bot.load(f"src.commands.staff.setup.tickets.{ext}") for ext in SETUP_TICKETS]

        # Partie listeners
        [self.bot.load(f"src.listeners.{ext}") for ext in LISTENERS]
        [self.bot.load(f"src.listeners.logs.{ext}") for ext in LISTENERS_LOGS]
        [self.bot.load(f"src.listeners.report.{ext}") for ext in LISTENERS_REPORT]
        [self.bot.load(f"src.listeners.suggestion.{ext}") for ext in LISTENERS_SUGGEST]
        [self.bot.load(f"src.listeners.ticket.{ext}") for ext in LISTENERS_TICKET]


if __name__ == '__main__':
    Main()
