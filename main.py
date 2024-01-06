import interactions
from dotenv import load_dotenv

load_dotenv()

from src.utils.const import *


class Main:
    def __init__(self):
        self.bot = interactions.Client(
            intents=interactions.Intents.ALL,
            status=interactions.Status.DO_NOT_DISTURB,
            activity=interactions.Activity.create(
                name="sa réparation",
                type=interactions.ActivityType.COMPETING
            ),
            send_command_tracebacks=False,
            owner_ids=[700685199662514186]
        )
        self.setup()
        self.bot.start(TOKEN)

    def setup(self):
        # Partie commandes
        self.bot.load_extension("src.commands.staff.self_role")
        self.bot.load_extension("src.commands.staff.setup.setup")
        self.bot.load_extension("src.commands.mudae.auto_rolls")
        [self.bot.load_extension(f"src.commands.{ext}") for ext in COMMANDS]
        [self.bot.load_extension(f"src.commands.ticket.{ext}") for ext in COMMANDS_TICKET]
        # [self.bot.load(f"src.commands.staff.{ext}") for ext in COMMANDS_STAFF]
        [self.bot.load_extension(f"src.commands.staff.mod.{ext}") for ext in COMMANDS_MOD]
        [self.bot.load_extension(f"src.commands.staff.admin.{ext}") for ext in COMMANDS_ADMIN]
        # [self.bot.load(f"src.commands.staff.setup.{ext}") for ext in COMMANDS_SETUP]
        # [self.bot.load(f"src.commands.staff.setup.roles.{ext}") for ext in SETUP_ROLES]
        # [self.bot.load(f"src.commands.staff.setup.channels.{ext}") for ext in SETUP_CHANNELS]
        # [self.bot.load(f"src.commands.staff.setup.tickets.{ext}") for ext in SETUP_TICKETS]
        [self.bot.load_extension(f"src.commands.staff.plugins.{ext}") for ext in PLUGINS]
        #
        # # Partie listeners
        [self.bot.load_extension(f"src.listeners.{ext}") for ext in LISTENERS]
        [self.bot.load_extension(f"src.listeners.logs.{ext}") for ext in LISTENERS_LOGS]
        [self.bot.load_extension(f"src.listeners.suggestion.{ext}") for ext in LISTENERS_SUGGEST]
        [self.bot.load_extension(f"src.listeners.ticket.{ext}") for ext in LISTENERS_TICKET]
        [self.bot.load_extension(f"src.listeners.update_db.{ext}") for ext in UPDATE_DB]
        # [self.bot.load_extension(f"src.listeners.report.{ext}") for ext in LISTENERS_REPORT]


if __name__ == '__main__':
    Main()
