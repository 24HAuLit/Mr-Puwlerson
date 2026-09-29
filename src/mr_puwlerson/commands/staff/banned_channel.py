import sqlite3
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands


def localized(english: str, french: str) -> app_commands.locale_str:
    return app_commands.locale_str(english, french=french)


class StaffTranslator(app_commands.Translator):
    async def translate(self, string, locale, context):
        if locale == discord.Locale.french:
            return string.extras.get("french")
        return None


async def install_translator(bot: commands.Bot):
    if bot.tree.translator is None:
        await bot.tree.set_translator(StaffTranslator())


def _locale(guild_id: int) -> str:
    with sqlite3.connect(f"./Database/{guild_id}.db") as conn:
        return conn.execute("SELECT locale FROM config").fetchone()[0]


async def database_ready(interaction: discord.Interaction) -> bool:
    if interaction.guild is None:
        return False
    if not Path(f"./Database/{interaction.guild.id}.db").exists():
        await interaction.response.send_message(
            f"Database not found for ID `{interaction.guild.id}`. This server is not configured yet.",
            ephemeral=True,
        )
        return False
    return True


def error_message(guild_id: int, kind: str, value: str = "") -> str:
    french = _locale(guild_id) == "fr"
    if kind == "permission":
        return ":x: Vous n'avez pas la permission de faire ceci." if french else ":x: You don't have the permission to do this."
    if kind == "plugin":
        return (f":x: Désolé, mais le plugin `{value}` est désactivé sur ce serveur."
                if french else f":x: Sorry, but the plugin `{value}` is disabled on this server.")
    if kind == "blacklisted":
        return (":x: Désolé, mais cet utilisateur est déjà blacklist."
                if french else ":x: Sorry, but this user is already blacklist.")
    if kind == "giveaway_started":
        return (":x: Un giveaway est déjà en cours !"
                if french else ":x: A giveaway is already started !")
    if kind == "message_not_found":
        return (f":x: Le message qui a pour ID `{value}` n'existe pas dans ce salon. Veuillez vérifier que le message est bien dans ce salon ou que le message existe bien."
                if french else f":x: The message with the ID `{value}` does not exist in this channel. Please check that the message is in this channel or if it exists.")
    raise ValueError(kind)


async def has_permission(interaction: discord.Interaction, role_column: str) -> bool:
    guild = interaction.guild
    member = interaction.user
    if guild is None or not isinstance(member, discord.Member):
        return False
    if guild.owner_id == member.id:
        return True
    with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
        owner_role, other_role = conn.execute(
            f"SELECT owner_role, {role_column} FROM config"
        ).fetchone()
    member_role_ids = {role.id for role in member.roles}
    if owner_role in member_role_ids or other_role in member_role_ids:
        return True
    await interaction.response.send_message(error_message(guild.id, "permission"), ephemeral=True)
    return False


async def plugin_ready(interaction: discord.Interaction, plugin: str) -> bool:
    guild = interaction.guild
    if guild is None:
        return False
    with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
        enabled = conn.execute("SELECT status FROM plugins WHERE name = ?", (plugin,)).fetchone()
    if enabled is not None and enabled[0] == "true":
        return True
    await interaction.response.send_message(
        error_message(guild.id, "plugin", plugin), ephemeral=True
    )
    return False


class BannedChannels(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="banned_channels", description=localized("Allows you to add/ delete a 'banned channel'", "Permet d'ajouter/ supprimer un salon bannis"))
    @app_commands.guild_only()
    @app_commands.rename(channel=localized("channel", "salon"))
    @app_commands.describe(channel=localized("Channel that will (not) have logs.", "Salon qui aura/ n'aura pas de logs."))
    async def banned_channels(self, interaction: discord.Interaction, channel: discord.abc.GuildChannel):
        if not await database_ready(interaction) or not await has_permission(interaction, "owner_role"):
            return

        guild = interaction.guild
        if guild is None:
            return
        with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
            row = conn.execute("SELECT hidden FROM channels WHERE id = ?", (channel.id,)).fetchone()
            if row is None:
                await interaction.response.send_message("Ce salon n'est pas configuré.", ephemeral=True)
                return
            hidden = 0 if row[0] == 1 else 1
            conn.execute("UPDATE channels SET hidden = ? WHERE id = ?", (hidden, channel.id))
        message = (f"Le salon `{channel.name}` sera désormais affiché dans les logs."
                   if hidden == 0 else f"Le salon `{channel.name}` ne sera plus affiché dans les logs.")
        await interaction.response.send_message(message, ephemeral=True)


async def setup(bot: commands.Bot):
    await install_translator(bot)
    await bot.add_cog(BannedChannels(bot))
