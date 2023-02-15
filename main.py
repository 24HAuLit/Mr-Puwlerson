import interactions
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
        # [self.bot.load(f"src.{root.replace(f'{src_path2}/', '')}.{ext.replace('.py', '')}")
        #  for root, dirs, files in os.walk(f"{src_path2}/{directory}")
        #  for ext in files
        #  if ext.endswith(".py")]
        [self.bot.load(f"src.commands.{ext}") for ext in COMMANDS]
        [self.bot.load(f"src.commands.staff.{ext}") for ext in COMMANDS_STAFF]
        [self.bot.load(f"src.commands.ticket.{ext}") for ext in COMMANDS_TICKET]
        [self.bot.load(f"src.commands.staff.setup.{ext}") for ext in COMMANDS_SETUP]
        [self.bot.load(f"src.commands.staff.setup.roles.{ext}") for ext in SETUP_ROLES]

        # Partie listeners
        [self.bot.load(f"src.listeners.{ext}") for ext in LISTENERS]
        [self.bot.load(f"src.listeners.logs.{ext}") for ext in LISTENERS_LOGS]
        [self.bot.load(f"src.listeners.report.{ext}") for ext in LISTENERS_REPORT]
        [self.bot.load(f"src.listeners.suggestion.{ext}") for ext in LISTENERS_SUGGEST]
        [self.bot.load(f"src.listeners.ticket.{ext}") for ext in LISTENERS_TICKET]


if __name__ == '__main__':
    Main()
