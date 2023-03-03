class ErrorMessage:
    def __init__(self):
        pass

    @staticmethod
    def database_not_found(guild_id):
        """Send a message when the database is not found for the guild ID.
        :param guild_id: The guild ID."""

        return f"La base de donnée n'a pas été trouvé pour l'ID `{guild_id}`. Le serveur n'a pas encore été configuré."

    @staticmethod
    def MissingPermissions():
        """Send a message when the user doesn't have the permission to use the command/ component."""
        return ":x: Vous n'avez pas la permission de faire ceci."

    @staticmethod
    def OwnerOnly():
        """Send a message when the user doesn't have the permission to use the command only for guild owner."""
        return ":x: Vous n'avez pas la permission d'utiliser cette commande. Seul le propriétaire du serveur peut l'utiliser."

    @staticmethod
    def MissingRequiredArgument(arguments: str):
        """Send a message when the user doesn't specify the required argument.
        :param arguments: The arguments name."""
        return f":x: Vous devez spécifier un/ des argument(s) : `{arguments}`."

    @staticmethod
    def ChannelError():
        """Send a message when the user use the command in a wrong channel"""
        return f":x: Vous ne pouvez pas utiliser cette commande dans ce salon."

    @staticmethod
    def PluginError(plugin_name: str):
        """Send a message when the plugin is disabled."""
        return f":x: Désolé, mais le plugin `{plugin_name}` est désactivé sur ce serveur."

    @staticmethod
    def BlacklistError():
        """Send a message when the user is in the blacklist."""
        return ":x: Désolé, mais vous êtes blacklist. Vous ne pouvez donc pas effectuer cette action."

