import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.coinflip import enable_french_localizations
from mr_puwlerson.utils.const import commands_list

# Title, description, usage (French and English) from the existing help messages.
HELP_DETAILS = {
    "ping": ("ping", "Permet de voir le ping du bot.", "Allows you to see the bot's ping.",
             "/ping", "/ping", None),
    "pileface": ("pileface", "Permet de lancer une pièce.", "Allows you to throw a coin.",
                 "/pileface", "/pileface", None),
    "suggest": ("suggest", "Permet d'envoyer une suggestion.", "Allows you to send a suggestion.",
                "/suggest <suggestion>", "/suggest <suggestion>", None),
    "mod clear": ("clear", "Permet de supprimer un certain nombre de messages.",
                  "Allows you to delete a certain number of messages.",
                  "/mod clear <nombre de message>", "/mod clear <number of messages>", "staff_role"),
    "mod timeout": ("timeout", "Permet de mettre un utilisateur en timeout.",
                    "Allows you to put a user in timeout.",
                    "/mod timeout <@utilisateur> <durée>", "/mod timeout <User> <duration>", "staff_role"),
    "mod untimemout": ("untimeout", "Permet de retirer le timeout d'un utilisateur.",
                       "Allows you to remove the timeout from a user.",
                       "/mod untimeout <@utilisateur>", "/mod untimeout <User>", "staff_role"),
    "nuke": ("nuke", "Permet de supprimer tous les messages d'un salon.",
             "Allows you to delete all messages from a channel.", "/mod nuke", "/mod nuke", "admin_role"),
    "blacklist": ("blacklist", "Permet de mettre un utilisateur en blacklist.",
                  "Allows you to put a user in blacklist.",
                  "/blacklist <@utilisateur> <raison>", "/blacklist <User> <Reason>", "admin_role"),
    "unblacklist": ("unblacklist", "Permet de retirer un utilisateur de la blacklist.",
                    "Allows you to remove a user from the blacklist.",
                    "/unblacklist <@utilisateur> [raison]", "/unblacklist <User> [reason]", "admin_role"),
    "giveaway": ("giveaway", "Permet de faire un giveaway.", "Allows you to make a giveaway.",
                 "/giveaway <gain> <nb gagnants> <temps>",
                 "/giveaway <prize> <number of winners> <time>", "admin_role"),
    "setup server": ("setup_server", "Permet de configurer les bases de données du serveur.",
                     "Allows you to configure databases of the server.",
                     "/setup_server", "/setup_server", "owner_role"),
}

FOOTER_FR = "Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
FOOTER_EN = "This bot uses slash-commands, so you have to put a / at the beginning of each one."
DEFAULT = "```\n• help\n• ping\n• pileface\n• suggest\n```"
STAFF = "```\n• mod clear\n• mod timeout\n• mod untimemout\n```"
ADMIN = "```\n• nuke\n• blacklist\n• unblacklist\n• Giveaway\n```"
OWNER = "```• setup server\n• setup roles\n• setup channels\n• setup tickets\n• setup max_ticket\n• locale\n• update```"
TICKET = "```\n• add\n• remove\n• rename\n• close\n• close_reason\n```"


def detailed_help(command: str, guild: discord.Guild, user: discord.User | discord.Member,
                  cursor: sqlite3.Cursor) -> discord.Embed:
    name, fr_description, en_description, fr_usage, en_usage, role_column = HELP_DETAILS[command]
    locale = cursor.execute("SELECT locale FROM config").fetchone()[0]
    french = locale == "fr"
    em = discord.Embed(title=f"Commande `{name}`" if french else f"`{name}` Command",
                       description=fr_description if french else en_description,
                       color=0x00FFEE, timestamp=datetime.now(UTC))
    if role_column is None:
        permission = "Aucune" if french else "Default"
    else:
        role_id = cursor.execute(f"SELECT {role_column} FROM config").fetchone()[0]
        role = guild.get_role(role_id)
        role_name = role.name if role is not None else f"<@&{role_id}>"
        permission = f"Rôle {role_name}" if french else f"{role_name} role"
    em.add_field(name="**Permission**", value=f"```\n• {permission}\n```", inline=True)
    usage = fr_usage if french else en_usage
    usage = f"```\n• {usage}\n```"
    if command == "mod clear":
        usage += "\n• Par défaut, le nombre de message est de 5." if french else "\n• By default, the number of messages is 5."
    elif command == "giveaway":
        usage += "\n• Le temps est en secondes" if french else "\n • The time is in seconds"
    em.add_field(name="**Utilisation**" if french else "**Usage**", value=usage, inline=True)
    em.set_footer(icon_url=user.display_avatar.url, text=FOOTER_FR if french else FOOTER_EN)
    return em


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description=app_commands.locale_str("To have all the commands at hand.",
                                            fr="Pour avoir toutes les commandes à porter de main."),
    )
    @app_commands.guild_only()
    @app_commands.describe(command=app_commands.locale_str("To get information on a command.",
                                         fr="Pour avoir des informations sur une commande."))
    @app_commands.choices(command=[app_commands.Choice(name=name, value=name) for name in commands_list])
    async def help(self, interaction: discord.Interaction, command: str | None = None):
        guild = interaction.guild
        if guild is None or not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        path = Path(f"./Database/{guild.id}.db")
        if not path.exists():
            await interaction.response.send_message(
                f"Database not found for ID `{guild.id}`. This server is not configured yet.", ephemeral=True
            )
            return

        with sqlite3.connect(path) as conn:
            c = conn.cursor()
            if command in HELP_DETAILS:
                em = detailed_help(command, guild, interaction.user, c)
            else:
                owner_role = c.execute("SELECT owner_role FROM config").fetchone()[0]
                admin_role = c.execute("SELECT admin_role FROM config").fetchone()[0]
                staff_role = c.execute("SELECT staff_role FROM config").fetchone()[0]
                role_ids = {role.id for role in interaction.user.roles}
                em = discord.Embed(title="📑 Liste des commandes", color=0x00FFEE,
                                   timestamp=datetime.now(UTC))
                if interaction.user.id == guild.owner_id or owner_role in role_ids:
                    sections = (("Default", DEFAULT), ("Staff", STAFF), ("Admin", ADMIN),
                                ("Owner", OWNER), ("Ticket", TICKET))
                elif admin_role in role_ids:
                    sections = (("Default", DEFAULT), ("Staff", STAFF), ("Admin", ADMIN), ("Ticket", TICKET))
                elif staff_role in role_ids:
                    sections = (("Default", DEFAULT), ("Staff", STAFF), ("Ticket", TICKET))
                else:
                    suggest = c.execute("SELECT suggest_channel FROM config").fetchone()[0]
                    em = discord.Embed(
                        title="📑 Liste des commandes",
                        description="• help | **Permet de connaître toutes les commandes du serveur.**\n"
                                    "• ping | **Pong!**\n• pileface | **Permet de lancer une pièce (Pile ou Face)**\n"
                                    f"• suggest | **Pour pouvoir poster une suggestion dans <#{suggest}>** ",
                        color=0x00FFEE, timestamp=datetime.now(UTC),
                    )
                    sections = ()
                for title, value in sections:
                    em.add_field(name=f"**{title}**", value=value, inline=True)
                em.set_footer(icon_url=interaction.user.display_avatar.url, text=FOOTER_FR)

        await interaction.response.send_message(embed=em, ephemeral=True)


async def setup(bot: commands.Bot):
    await enable_french_localizations(bot)
    await bot.add_cog(Help(bot))
