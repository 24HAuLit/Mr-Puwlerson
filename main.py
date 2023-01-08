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
        self.bot.load("src.listeners.auto-role")
        self.bot.load("src.listeners.presence")
        # self.bot.load("listeners.bda.besoin-aide") # Il faut faire le delete de channel quand personne

        # Listeners report
        self.bot.load("src.listeners.report.report")
        self.bot.load("src.listeners.report.cancel")

        # Listeners logs
        self.bot.load("src.listeners.logs.message")
        self.bot.load("src.listeners.logs.join-quit")
        self.bot.load("src.listeners.logs.ban")

        # Listeners ticket
        self.bot.load("src.listeners.ticket.open_ticket")
        self.bot.load("src.listeners.ticket.claim_ticket")
        self.bot.load("src.listeners.ticket.close_ticket")
        self.bot.load("src.listeners.ticket.confirm_close")
        self.bot.load("src.listeners.ticket.close_reason")

        # Listeners suggestion
        self.bot.load("src.listeners.suggestion.accepted_suggest")
        self.bot.load("src.listeners.suggestion.denied_suggest")
        self.bot.load("src.listeners.suggestion.modal.modal_accept")
        self.bot.load("src.listeners.suggestion.modal.modal_deny")


    def setup_cmd(self):
        # Commande globale
        self.bot.load("src.commands.help")
        self.bot.load("src.commands.ping")
        self.bot.load("src.commands.suggest")
        self.bot.load("src.commands.userinfo")
        self.bot.load("src.commands.pileface")
        # self.bot.load("commands.embed") # Useless

        # Commande staff
        self.bot.load("src.commands.staff.nuke")
        self.bot.load("src.commands.staff.mod")
        self.bot.load("src.commands.staff.blacklist")
        self.bot.load("src.commands.staff.unblacklist")

        # Commande ticket
        self.bot.load("src.commands.ticket.add")
        self.bot.load("src.commands.ticket.claim_command")
        self.bot.load("src.commands.ticket.unclaim")
        self.bot.load("src.commands.ticket.close")
        self.bot.load("src.commands.ticket.close-reason")
        self.bot.load("src.commands.ticket.remove")
        self.bot.load("src.commands.ticket.rename")


if __name__ == '__main__':
    Main()
