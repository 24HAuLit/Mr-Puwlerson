import asyncio
import sqlite3
from datetime import UTC, datetime

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.ticket.tickets import (
    check_ticket,
    ensure_ticket_translator,
    register_ticket_commands,
    unregister_ticket_commands,
)


class ConfirmCloseView(discord.ui.View):
    def __init__(self, bot: commands.Bot, reason: str):
        super().__init__(timeout=900)
        self.bot = bot
        self.reason = reason

    @discord.ui.button(
        label="🔒 Confirmer la fermeture", style=discord.ButtonStyle.danger, custom_id="confirm_close_cmd"
    )
    async def confirm_close(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if not await check_ticket(interaction):
            return
        button.disabled = True
        await interaction.response.edit_message(view=self)
        channel = interaction.channel
        guild = interaction.guild
        assert isinstance(channel, discord.TextChannel) and guild is not None
        with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
            row = conn.execute("SELECT * FROM ticket WHERE channel_id = ?", (channel.id,)).fetchone()
            conn.execute("UPDATE ticket_count SET count = count - 1 WHERE user_id = ?", (row[1],))
            logs_id = conn.execute("SELECT id FROM logs_channels WHERE name = 'close'").fetchone()[0]

        await interaction.followup.send(
            embed=discord.Embed(description="**Transcript HS** pour une durée indéterminée.", color=0xFF0000)
        )
        await interaction.followup.send(
            embed=discord.Embed(description="Ce ticket va être fermé dans quelques instant...", color=0xFF0000)
        )
        await asyncio.sleep(5)
        await channel.delete()

        embed = discord.Embed(
            title="Fermeture de ticket", description="Un ticket a été fermé.",
            color=0xFF4646, timestamp=datetime.now(UTC),
        )
        embed.add_field(name="__**Ticket ID**__", value=str(row[0]), inline=True)
        embed.add_field(name="__**Ouvert par**__", value=f"<@{row[1]}>", inline=True)
        embed.add_field(name="__**Fermé par**__", value=interaction.user.mention, inline=True)
        if row[2] != "None":
            embed.add_field(name="__**Claim par**__", value=f"<@{row[2]}>", inline=True)
        embed.add_field(name="__**Raison**__", value=self.reason, inline=True)
        logs = self.bot.get_channel(int(logs_id))
        if logs is None:
            raise RuntimeError(f"Close log channel {logs_id} is unavailable")
        if not isinstance(logs, discord.abc.Messageable):
            raise TypeError(f"Close log channel {logs_id} cannot receive messages")
        await logs.send(embed=embed)
        self.stop()


class CloseTicketCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_unload(self) -> None:
        unregister_ticket_commands(self.bot, "close")

    @app_commands.command(name="close", description=app_commands.locale_str(
        "To close a ticket", french="Pour fermer un ticket"
    ))
    @app_commands.describe(reason=app_commands.locale_str("Reason to close", french="Raison de la fermeture"))
    @app_commands.rename(reason=app_commands.locale_str("reason", french="raison"))
    @app_commands.guild_only()
    async def close(self, interaction: discord.Interaction, reason: str = "Aucune raison.") -> None:
        if not await check_ticket(interaction):
            return
        await interaction.response.send_message(
            "Êtes-vous sur de vouloir fermer ce ticket ?",
            view=ConfirmCloseView(self.bot, reason), ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    cog = CloseTicketCommand(bot)
    await bot.add_cog(cog)
    await ensure_ticket_translator(bot)
    await register_ticket_commands(bot, cog, "close")
