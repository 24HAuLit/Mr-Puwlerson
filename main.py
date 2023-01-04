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
        interactions.ext.voice.setup(self.bot)
        self.setup_listeners()
        self.setup_cmd()

        self.bot.start()

    def setup_listeners(self):
        # Listeners globaux
        self.bot.load("listeners.auto-role")
        self.bot.load("listeners.presence")
        # self.bot.load("listeners.bda.besoin-aide") # Faut faire le delete de channel quand personne

        # Listerners report
        self.bot.load("listeners.report.report")
        self.bot.load("listeners.report.cancel")

        # Listeners logs
        self.bot.load("listeners.logs.message")
        self.bot.load("listeners.logs.join-quit")
        self.bot.load("listeners.logs.ban")

        # Listeners ticket
        self.bot.load("listeners.ticket.open_ticket")
        self.bot.load("listeners.ticket.claim_ticket")
        self.bot.load("listeners.ticket.close_ticket")
        self.bot.load("listeners.ticket.confirm_close")
        self.bot.load("listeners.ticket.close_reason")

        # Listeners suggestion
        self.bot.load("listeners.suggestion.accepted_suggest")
        self.bot.load("listeners.suggestion.denied_suggest")
        self.bot.load("listeners.suggestion.modal.modal_accept")
        self.bot.load("listeners.suggestion.modal.modal_deny")

    def setup_cmd(self):
        # Commande globale
        self.bot.load("commands.help")
        self.bot.load("commands.ping")
        self.bot.load("commands.suggest")
        self.bot.load("commands.userinfo")
        self.bot.load("commands.pileface")
        # self.bot.load("commands.embed") # Useless

        # Commande staff
        self.bot.load("commands.staff.nuke")
        self.bot.load("commands.staff.mod")

        # Commande ticket
        self.bot.load("commands.ticket.add")
        self.bot.load("commands.ticket.claim_command")
        self.bot.load("commands.ticket.unclaim")
        self.bot.load("commands.ticket.close")
        self.bot.load("commands.ticket.close-reason")
        self.bot.load("commands.ticket.remove")
        self.bot.load("commands.ticket.rename")


if __name__ == '__main__':
    Main()
