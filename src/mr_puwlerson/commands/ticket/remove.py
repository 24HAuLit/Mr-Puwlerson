import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.ticket.tickets import check_ticket, ensure_ticket_translator

_TICKET_DENY = discord.Permissions(2199023255551)


class RemoveMember(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="remove", description="Remove a user or a role from the ticket")
    @app_commands.describe(option=app_commands.locale_str(
        "To remove a user or a role to the ticket.",
        french="Pour retirer un utilisateur ou un role au ticket.",
    ))
    @app_commands.guild_only()
    async def remove(self, interaction: discord.Interaction, option: discord.Member | discord.Role) -> None:
        if not await check_ticket(interaction):
            return

        channel = interaction.channel
        assert isinstance(channel, discord.TextChannel)
        await channel.set_permissions(
            option, overwrite=discord.PermissionOverwrite.from_pair(discord.Permissions.none(), _TICKET_DENY)
        )
        await interaction.response.send_message(
            embed=discord.Embed(description=f"{option.mention} a été retiré du ticket.", color=0xFF5A5A)
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RemoveMember(bot))
    await ensure_ticket_translator(bot)
