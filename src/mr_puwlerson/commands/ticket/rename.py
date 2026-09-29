import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.ticket.tickets import check_ticket, ensure_ticket_translator


class Rename(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="rename", description=app_commands.locale_str(
        "To rename a ticket", french="Pour renommer un ticket"
    ))
    @app_commands.describe(name=app_commands.locale_str(
        "New name for the ticket", french="Nouveau nom pour le ticket"
    ))
    @app_commands.rename(name=app_commands.locale_str("name", french="nom"))
    @app_commands.guild_only()
    async def rename(self, interaction: discord.Interaction, name: str) -> None:
        if not await check_ticket(interaction):
            return

        channel = interaction.channel
        assert isinstance(channel, discord.TextChannel)
        await channel.edit(name=name)
        await interaction.response.send_message(f"Le ticket vient d'être renommé **{name}**.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Rename(bot))
    await ensure_ticket_translator(bot)
