import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.ticket.tickets import (
    check_ticket,
    ensure_ticket_translator,
    register_ticket_commands,
    ticket_message,
    unregister_ticket_commands,
)

_TICKET_ALLOW = discord.Permissions(64 | 1024 | 2048 | 32768 | 65536 | 262144 | 2147483648)


class AddMember(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_unload(self) -> None:
        unregister_ticket_commands(self.bot, "add")

    @app_commands.command(name="add", description=app_commands.locale_str(
        "To add someone or a role to the ticket.",
        french="Pour pouvoir ajouter quelqu'un ou un role au ticket.",
    ))
    @app_commands.describe(option=app_commands.locale_str(
        "To add a user or a role to the ticket.",
        french="Pour ajouter un utilisateur ou un role au ticket.",
    ))
    @app_commands.guild_only()
    async def add(self, interaction: discord.Interaction, option: discord.Member | discord.Role) -> None:
        if not await check_ticket(interaction):
            return

        channel = interaction.channel
        guild = interaction.guild
        assert isinstance(channel, discord.TextChannel) and guild is not None
        if isinstance(option, discord.Member):
            if guild.get_member(option.id) is None:
                await interaction.response.send_message(
                    ticket_message(guild.id,
                                   f":x: L'utilisateur `{option.name}` n'existe pas ou n'est pas sur le serveur. Veuillez verifier que l'utilisateur est bien sur ce serveur.",
                                   f":x: The user `{option.name}` does not exist or is not on the server. Please check that the user is on this server."),
                    ephemeral=True,
                )
                return
            if any(member.id == option.id for member in channel.members):
                await interaction.response.send_message(
                    ticket_message(guild.id,
                                   f":x: L'utilisateur `{option.name}` est déjà dans ce ticket.",
                                   f":x: The user `{option.name}` is already in this ticket."),
                    ephemeral=True,
                )
                return
        else:
            if guild.get_role(option.id) is None:
                await interaction.response.send_message(
                    ticket_message(guild.id,
                                   f":x: Le role `{option}` n'existe pas sur le serveur. Veuillez verifier que le role existe bien sur ce serveur.",
                                   f":x: The role `{option}` does not exist  on the server. Please check that the role exists on this server."),
                    ephemeral=True,
                )
                return
            if channel.permissions_for(option).view_channel:
                await interaction.response.send_message("test", ephemeral=True)
                return

        await channel.set_permissions(
            option, overwrite=discord.PermissionOverwrite.from_pair(_TICKET_ALLOW, discord.Permissions.none())
        )
        await interaction.response.send_message(
            embed=discord.Embed(description=f"{option.mention} a été ajouter au ticket.", color=0x2ECC70)
        )


async def setup(bot: commands.Bot) -> None:
    cog = AddMember(bot)
    await bot.add_cog(cog)
    await ensure_ticket_translator(bot)
    await register_ticket_commands(bot, cog, "add")
