import sqlite3
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

ticket = app_commands.guild_only(app_commands.Group(name="ticket", description="Ticket commands"))


class TicketTranslator(app_commands.Translator):
    def __init__(self, previous: app_commands.Translator | None = None):
        self.previous = previous

    async def load(self) -> None:
        if self.previous is not None:
            await self.previous.load()

    async def unload(self) -> None:
        if self.previous is not None:
            await self.previous.unload()

    async def translate(self, string, locale, context):
        if locale == discord.Locale.french and "french" in string.extras:
            return string.extras["french"]
        if self.previous is not None:
            return await self.previous.translate(string, locale, context)
        return None


async def ensure_ticket_translator(bot: commands.Bot) -> None:
    current = bot.tree.translator
    if not isinstance(current, TicketTranslator):
        await bot.tree.set_translator(TicketTranslator(current))


async def register_ticket_commands(bot: commands.Bot, cog: commands.Cog, *names: str) -> None:
    """Attach commands from separately loaded cogs to the shared /ticket group."""
    group = bot.tree.get_command("ticket")
    if group is None:
        bot.tree.add_command(ticket)
        group = ticket
    if not isinstance(group, app_commands.Group):
        raise TypeError("/ticket must be a slash command group")
    for command in cog.get_app_commands():
        if command.name in names:
            bot.tree.remove_command(command.name)
            group.add_command(command)


def unregister_ticket_commands(bot: commands.Bot, *names: str) -> None:
    group = bot.tree.get_command("ticket")
    if isinstance(group, app_commands.Group):
        for name in names:
            group.remove_command(name)


def ticket_message(guild_id: int, french: str, english: str) -> str:
    with sqlite3.connect(f"./Database/{guild_id}.db") as conn:
        locale = conn.execute("SELECT locale FROM config").fetchone()[0]
    return french if locale == "fr" else english


async def check_ticket(interaction: discord.Interaction, *, staff_error: bool = True) -> bool:
    guild = interaction.guild
    if guild is None:
        return False
    if not Path(f"./Database/{guild.id}.db").exists():
        await interaction.response.send_message(
            f"Database not found for ID `{guild.id}`. This server is not configured yet.", ephemeral=True
        )
        return False

    with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
        owner_role, staff_role, parent_id = conn.execute(
            "SELECT owner_role, staff_role, ticket_parent FROM config"
        ).fetchone()
    member = interaction.user
    if not isinstance(member, discord.Member) or not (
        member.id == guild.owner_id or any(role.id in (owner_role, staff_role) for role in member.roles)
    ):
        if staff_error:
            await interaction.response.send_message(
                ticket_message(guild.id, ":x: Vous n'avez pas la permission de faire ceci.",
                               ":x: You don't have the permission to do this."), ephemeral=True
            )
        return False

    channel = interaction.channel
    if not isinstance(channel, discord.TextChannel) or channel.category_id != parent_id:
        await interaction.response.send_message(
            ticket_message(guild.id, ":x: Vous ne pouvez pas utiliser cette commande dans ce salon.",
                           ":x: You cannot use this command in this channel."), ephemeral=True
        )
        return False
    return True


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tickets(bot))
    await ensure_ticket_translator(bot)
    if bot.tree.get_command("ticket") is None:
        bot.tree.add_command(ticket)
