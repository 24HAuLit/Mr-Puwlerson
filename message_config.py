from os.path import exists
from sqlite3 import connect


class ErrorMessage:
    def __init__(self):
        pass

    @staticmethod
    def database_not_found(guild_id):
        """Send a message when the database is not found for the guild ID.
        :param guild_id: The guild ID."""
        return f"Database not found for ID `{guild_id}`. This server is not configured yet."

    @staticmethod
    def MissingPermissions(guild_id):
        """Send a message when the user doesn't have the permission to use the command/ component.
        :param guild_id:"""
        if exists(f"./Database/{guild_id}.db") is False:
            return
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                return ":x: Vous n'avez pas la permission de faire ceci."
            elif locale == 'en':
                return ":x: You don't have the permission to do this."

    @staticmethod
    def OwnerOnly(guild_id):
        """Send a message when the user doesn't have the permission to use the command only for guild owner.
        :param guild_id: """
        if exists(f"./Database/{guild_id}.db") is False:
            return
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                return ":x: Vous n'avez pas la permission d'utiliser cette commande. Seul le propriétaire du serveur " \
                       "peut l'utiliser."
            elif locale == 'en':
                return ":x: You don't have the permission to use this command. Only the server owner can use it."

    @staticmethod
    def MissingRequiredArgument(guild_id, arguments: str):
        """Send a message when the user doesn't specify the required argument.
        :param guild_id:
        :param arguments: The arguments name."""
        if exists(f"./Database/{guild_id}.db") is False:
            return
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                return f":x: Vous devez spécifier un/ des argument(s) : `{arguments}`."
            elif locale == 'en':
                return f":x: You must specify an/ some argument(s) : `{arguments}`."

    @staticmethod
    def ChannelError(guild_id):
        """Send a message when the user use the command in a wrong channel
        :param guild_id: """
        if exists(f"./Database/{guild_id}.db") is False:
            return
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                return ":x: Vous ne pouvez pas utiliser cette commande dans ce salon."
            elif locale == 'en':
                return ":x: You can't use this command in this channel."

    @staticmethod
    def PluginError(guild_id, plugin_name: str):
        """Send a message when the plugin is disabled.
        :param guild_id:
        :param plugin_name: The plugin name."""
        if exists(f"./Database/{guild_id}.db") is False:
            return
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                return f":x: Désolé, mais le plugin `{plugin_name}` est désactivé sur ce serveur."
            elif locale == 'en':
                return f":x: Sorry, but the plugin `{plugin_name}` is disabled on this server."

    @staticmethod
    def BlacklistError(guild_id):
        """Send a message when the user is in the blacklist.
        :param guild_id:"""
        if exists(f"./Database/{guild_id}.db") is False:
            return
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                return ":x: Désolé, mais vous êtes blacklist. Vous ne pouvez donc pas effectuer cette action."
            elif locale == 'en':
                return ":x: Sorry, but you are blacklist. You can't do this action."

    @staticmethod
    def ticket_limit(guild_id):
        """Send a message when the user has reached the limit of tickets.
        :param guild_id:"""
        if exists(f"./Database/{guild_id}.db") is False:
            return
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                return ":x: Vous avez atteint la limite de tickets."
            elif locale == 'en':
                return ":x: You have reached the ticket limit."

    @staticmethod
    def giveaway_already_started(guild_id):
        """Send a message when the giveaway is already started.
        :param guild_id:"""
        if exists(f"./Database/{guild_id}.db") is False:
            return
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                return ":x: Un giveaway est déjà en cours !"
            elif locale == 'en':
                return ":x: A giveaway is already started !"

    @staticmethod
    def cooldown(guild_id, time):
        """Send a message when the user is in cooldown.
        :param guild_id:
        :param time: The cooldown time."""
        if exists(f"./Database/{guild_id}.db") is False:
            return
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                return f":x: Vous êtes en cooldown. Veuillez patienter encore {time} minutes."
            elif locale == 'en':
                return f":x: You are in cooldown. Please wait {time} minutes."
