from datetime import datetime
from os.path import exists
from sqlite3 import connect

import interactions


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
            return ErrorMessage.database_not_found(guild_id)
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
            return ErrorMessage.database_not_found(guild_id)
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
            return ErrorMessage.database_not_found(guild_id)
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
            return ErrorMessage.database_not_found(guild_id)
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
            return ErrorMessage.database_not_found(guild_id)
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
            return ErrorMessage.database_not_found(guild_id)
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

    @staticmethod
    def MessageNotFound(guild_id, message_id):
        """Send a message when the message is not found.
        :param guild_id:
        :param message_id: The message id."""

        if exists(f"./Database/{guild_id}.db") is False:
            return ErrorMessage.database_not_found(guild_id)
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                return f":x: Le message qui a pour ID `{message_id}` n'existe pas dans ce salon. Veuillez vérifier " \
                       f"que le message est bien dans ce salon ou que le message existe bien."
            elif locale == 'en':
                return f":x: The message with the ID `{message_id}` does not exist in this channel. Please check " \
                       f"that the message is in this channel or if it exists."


class HelpMessage:
    def __init__(self):
        pass

    @staticmethod
    def ping(context, guild_id):
        """Send the ping command help message.
        :param context:
        :param guild_id:"""
        if exists(f"./Database/{guild_id}.db") is False:
            return ErrorMessage.database_not_found(guild_id)
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                em = interactions.Embed(
                    title="Commande `ping`",
                    description="Permet de voir le ping du bot.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value="```\n• Aucune\n```",
                    inline=True
                )
                em.add_field(
                    name="**Utilisation**",
                    value="```\n• /ping\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
                )

                return em

            elif locale == 'en':
                em = interactions.Embed(
                    title="`ping` Command",
                    description="Allows you to see the bot's ping.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value="```\n• Default\n```",
                    inline=True
                )
                em.add_field(
                    name="**Usage**",
                    value="```\n• /ping\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="This bot uses slash-commands, so you have to put a / at the beginning of each one."
                )
                return em

    @staticmethod
    def pileface(context, guild_id):
        """Send the pileface command help message.
        :param context:
        :param guild_id:"""
        if exists(f"./Database/{guild_id}.db") is False:
            return ErrorMessage.database_not_found(guild_id)
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                em = interactions.Embed(
                    title="Commande `pileface`",
                    description="Permet de lancer une pièce.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value="```\n• Aucune\n```",
                    inline=True
                )
                em.add_field(
                    name="**Utilisation**",
                    value="```\n• /pileface\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
                )

                return em
            elif locale == 'en':
                em = interactions.Embed(
                    title="`pileface` Command",
                    description="Allows you to throw a coin.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value="```\n• Default\n```",
                    inline=True
                )
                em.add_field(
                    name="**Usage**",
                    value="```\n• /pileface\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="This bot uses slash-commands, so you have to put a / at the beginning of each one."
                )
                return em

    @staticmethod
    def suggestions(context, guild_id):
        """Send the suggestions command help message.
        :param context:
        :param guild_id:"""
        if exists(f"./Database/{guild_id}.db") is False:
            return ErrorMessage.database_not_found(guild_id)
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                em = interactions.Embed(
                    title="Commande `suggest`",
                    description="Permet d'envoyer une suggestion.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value="```\n• Aucune\n```",
                    inline=True
                )
                em.add_field(
                    name="**Utilisation**",
                    value="```\n• /suggest <suggestion>\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
                )

                return em
            elif locale == 'en':
                em = interactions.Embed(
                    title="`suggest` Command",
                    description="Allows you to send a suggestion.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value="```\n• Default\n```",
                    inline=True
                )
                em.add_field(
                    name="**Usage**",
                    value="```\n• /suggest <suggestion>\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="This bot uses slash-commands, so you have to put a / at the beginning of each one."
                )
                return em

    @staticmethod
    def clear(context, permission_role_name, guild_id):
        """Send the clear command help message.
        :param context:
        :param permission_role_name:
        :param guild_id:"""

        if exists(f"./Database/{guild_id}.db") is False:
            return ErrorMessage.database_not_found(guild_id)
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                em = interactions.Embed(
                    title="Commande `clear`",
                    description="Permet de supprimer un certain nombre de messages.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value=f"```\n• Rôle {permission_role_name}\n```",
                    inline=True
                )
                em.add_field(
                    name="**Utilisation**",
                    value="```\n• /mod clear <nombre de message>\n```\n• Par défaut, le nombre de message est de 5.",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
                )
                return em
            elif locale == 'en':
                em = interactions.Embed(
                    title="`clear` Command",
                    description="Allows you to delete a certain number of messages.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value=f"```\n• {permission_role_name} role\n```",
                    inline=True
                )
                em.add_field(
                    name="**Usage**",
                    value="```\n• /mod clear <number of messages>\n```\n• By default, the number of messages is 5.",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="This bot uses slash-commands, so you have to put a / at the beginning of each one."
                )
                return em

    @staticmethod
    def timeout(context, permission_role_name, guild_id):
        """Send the timeout command help message.
        :param context:
        :param permission_role_name:
        :param guild_id:"""
        if exists(f"./Database/{guild_id}.db") is False:
            return ErrorMessage.database_not_found(guild_id)
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                em = interactions.Embed(
                    title="Commande `timeout`",
                    description="Permet de mettre un utilisateur en timeout.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value=f"```\n• Rôle {permission_role_name}\n```",
                    inline=True
                )
                em.add_field(
                    name="**Utilisation**",
                    value="```\n• /mod timeout <@utilisateur> <durée>\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
                )
                return em
            elif locale == 'en':
                em = interactions.Embed(
                    title="`timeout` Command",
                    description="Allows you to put a user in timeout.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value=f"```\n• {permission_role_name} role\n```",
                    inline=True
                )
                em.add_field(
                    name="**Usage**",
                    value="```\n• /mod timeout <User> <duration>\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="This bot uses slash-commands, so you have to put a / at the beginning of each one."
                )
                return em

    @staticmethod
    def untimeout(context, permission_role_name, guild_id):
        """Send the untimeout command help message.
        :param context:
        :param permission_role_name:
        :param guild_id:"""
        if exists(f"./Database/{guild_id}.db") is False:
            return ErrorMessage.database_not_found(guild_id)
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                em = interactions.Embed(
                    title="Commande `untimeout`",
                    description="Permet de retirer le timeout d'un utilisateur.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value=f"```\n• Rôle {permission_role_name}\n```",
                    inline=True
                )
                em.add_field(
                    name="**Utilisation**",
                    value="```\n• /mod untimeout <@utilisateur>\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
                )
                return em
            elif locale == 'en':
                em = interactions.Embed(
                    title="`untimeout` Command",
                    description="Allows you to remove the timeout from a user.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value=f"```\n• {permission_role_name} role\n```",
                    inline=True
                )
                em.add_field(
                    name="**Usage**",
                    value="```\n• /mod untimeout <User>\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="This bot uses slash-commands, so you have to put a / at the beginning of each one."
                )
                return em

    @staticmethod
    def nuke(context, permission_role_name, guild_id):
        """Send the nuke command help message.
        :param context:
        :param permission_role_name:
        :param guild_id:"""
        if exists(f"./Database/{guild_id}.db") is False:
            return ErrorMessage.database_not_found(guild_id)
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                em = interactions.Embed(
                    title="Commande `nuke`",
                    description="Permet de supprimer tous les messages d'un salon.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value=f"```\n• Rôle {permission_role_name}\n```",
                    inline=True
                )
                em.add_field(
                    name="**Utilisation**",
                    value="```\n• /mod nuke\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
                )
                return em
            elif locale == 'en':
                em = interactions.Embed(
                    title="`nuke` Command",
                    description="Allows you to delete all messages from a channel.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value=f"```\n• {permission_role_name} role\n```",
                    inline=True
                )
                em.add_field(
                    name="**Usage**",
                    value="```\n• /mod nuke\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="This bot uses slash-commands, so you have to put a / at the beginning of each one."
                )
                return em

    @staticmethod
    def blacklist(context, permission_role_name, guild_id):
        """Send the blacklist command help message.
        :param context:
        :param permission_role_name:
        :param guild_id:"""
        if exists(f"./Database/{guild_id}.db") is False:
            return ErrorMessage.database_not_found(guild_id)
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                em = interactions.Embed(
                    title="Commande `blacklist`",
                    description="Permet de mettre un utilisateur en blacklist.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value=f"```\n• Rôle {permission_role_name}\n```",
                    inline=True
                )
                em.add_field(
                    name="**Utilisation**",
                    value="```\n• /blacklist <@utilisateur> <raison>\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
                )
                return em
            elif locale == 'en':
                em = interactions.Embed(
                    title="`blacklist` Command",
                    description="Allows you to put a user in blacklist.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value=f"```\n• {permission_role_name} role\n```",
                    inline=True
                )
                em.add_field(
                    name="**Usage**",
                    value="```\n• /blacklist <User> <Reason>\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="This bot uses slash-commands, so you have to put a / at the beginning of each one."
                )
                return em

    @staticmethod
    def unblacklist(context, permission_role_name, guild_id):
        """Send the unblacklist command help message.
        :param context:
        :param permission_role_name:
        :param guild_id:"""
        if exists(f"./Database/{guild_id}.db") is False:
            return ErrorMessage.database_not_found(guild_id)
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                em = interactions.Embed(
                    title="Commande `unblacklist`",
                    description="Permet de retirer un utilisateur de la blacklist.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value=f"```\n• Rôle {permission_role_name}\n```",
                    inline=True
                )
                em.add_field(
                    name="**Utilisation**",
                    value="```\n• /unblacklist <@utilisateur> [raison]\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
                )
                return em
            elif locale == 'en':
                em = interactions.Embed(
                    title="`unblacklist` Command",
                    description="Allows you to remove a user from the blacklist.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value=f"```\n• {permission_role_name} role\n```",
                    inline=True
                )
                em.add_field(
                    name="**Usage**",
                    value="```\n• /unblacklist <User> [reason]\n```",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="This bot uses slash-commands, so you have to put a / at the beginning of each one."
                )
                return em

    @staticmethod
    def giveaway(context, permission_role_name, guild_id):
        """Send the giveaway command help message.
        :param context:
        :param permission_role_name:
        :param guild_id:"""
        if exists(f"./Database/{guild_id}.db") is False:
            return ErrorMessage.database_not_found(guild_id)
        else:
            conn = connect(f'./Database/{guild_id}.db')
            c = conn.cursor()

            c.execute("SELECT locale FROM locale")
            locale = c.fetchone()[0]
            conn.close()

            if locale == 'fr':
                em = interactions.Embed(
                    title="Commande `giveaway`",
                    description="Permet de faire un giveaway.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value=f"```\n• Rôle {permission_role_name}\n```",
                    inline=True
                )
                em.add_field(
                    name="**Utilisation**",
                    value="```\n• /giveaway <gain> <nb gagnants> <temps>\n```\n• Le temps est en secondes",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
                )
                return em
            elif locale == 'en':
                em = interactions.Embed(
                    title="`giveaway` Command",
                    description="Allows you to make a giveaway.",
                    color=0x00FFEE,
                    timestamp=datetime.utcnow()
                )
                em.add_field(
                    name="**Permission**",
                    value=f"```\n• {permission_role_name} role\n```",
                    inline=True
                )
                em.add_field(
                    name="**Usage**",
                    value="```\n• /giveaway <prize> <number of winners> <time>\n```\n • The time is in seconds",
                    inline=True
                )
                em.set_footer(
                    icon_url=context.member.user.avatar_url,
                    text="This bot uses slash-commands, so you have to put a / at the beginning of each one."
                )
                return em
