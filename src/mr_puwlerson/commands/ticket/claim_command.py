import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.ticket.tickets import (
    check_ticket,
    ensure_ticket_translator,
    register_ticket_commands,
    unregister_ticket_commands,
)


class ClaimCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_unload(self) -> None:
        unregister_ticket_commands(self.bot, "claim", "unclaim")

    @app_commands.command(name="claim", description=app_commands.locale_str(
        "To claim a ticket", french="Pour revendiquer un ticket"
    ))
    @app_commands.guild_only()
    async def claim(self, interaction: discord.Interaction) -> None:
        if not await check_ticket(interaction):
            return

        channel = interaction.channel
        guild = interaction.guild
        assert isinstance(channel, discord.TextChannel) and guild is not None
        with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
            row = conn.execute("SELECT * FROM ticket WHERE channel_id = ?", (channel.id,)).fetchone()
            staff_id = interaction.user.id
            if row[2] is None or row[2] == "None":
                conn.execute("UPDATE ticket SET staff_id = ? WHERE channel_id = ?", (staff_id, channel.id))
                conn.commit()
                embed = discord.Embed(
                    description=f"Le ticket a été pris en charge par {interaction.user.mention}.", color=0x2ECC70
                )
                await interaction.response.send_message(embed=embed)
            elif str(row[2]) == str(staff_id):
                await interaction.response.send_message("Vous avez déjà pris en charge ce ticket.", ephemeral=True)
            else:
                await interaction.response.send_message(
                    f"<@{row[2]}> a déjà pris en charge ce ticket.", ephemeral=True
                )

    @app_commands.command(name="unclaim", description=app_commands.locale_str(
        "To unclaim a ticket", french="Pour dé-revendiquer un ticket"
    ))
    @app_commands.guild_only()
    async def unclaim(self, interaction: discord.Interaction) -> None:
        if not await check_ticket(interaction, staff_error=False):
            return

        channel = interaction.channel
        guild = interaction.guild
        assert isinstance(channel, discord.TextChannel) and guild is not None
        with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
            row = conn.execute("SELECT * FROM ticket WHERE channel_id = ?", (channel.id,)).fetchone()
            staff_id = interaction.user.id
            if str(row[2]) == str(staff_id):
                conn.execute("UPDATE ticket SET staff_id = 'None' WHERE channel_id = ?", (channel.id,))
                conn.commit()
                embed = discord.Embed(
                    description=f"Le ticket n'est plus pris en charge par {interaction.user.mention}.",
                    color=0x2ECC70,
                )
                await interaction.response.send_message(embed=embed)
            elif row[2] is None or row[2] == "None":
                await interaction.response.send_message("Personne ne prend en charge ce ticket.", ephemeral=True)
            else:
                await interaction.response.send_message(
                    f"Vous ne pouvez pas faire ceci car <@{row[2]}> a pris ce ticket.", ephemeral=True
                )


async def setup(bot: commands.Bot) -> None:
    cog = ClaimCommand(bot)
    await bot.add_cog(cog)
    await ensure_ticket_translator(bot)
    await register_ticket_commands(bot, cog, "claim", "unclaim")
