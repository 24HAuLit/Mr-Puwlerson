import sqlite3
from datetime import UTC, datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.staff.banned_channel import (
    database_ready,
    has_permission,
    install_translator,
    localized,
)
from mr_puwlerson.utils.time_converter import time_to_readable


class Mod(commands.Cog):
    mod = app_commands.Group(name="mod", description="Moderation commands", guild_only=True)

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @mod.command(name="clear", description="Delete messages")
    @app_commands.rename(number=localized("number", "nombre"))
    @app_commands.describe(number=localized("Number of messages to delete. Default : 5",
                                             "Nombre de messages à supprimer. Par défaut : 5"))
    async def clear(self, interaction: discord.Interaction, number: int = 5):
        if not await database_ready(interaction) or not await has_permission(interaction, "staff_role"):
            return
        guild = interaction.guild
        channel = interaction.channel
        if guild is None or not isinstance(channel, (discord.TextChannel, discord.Thread)):
            await interaction.response.send_message("Cette commande nécessite un salon textuel.", ephemeral=True)
            return
        # The interaction must be acknowledged before a potentially slow purge.
        await interaction.response.defer(ephemeral=True)
        deleted = await channel.purge(limit=number)
        em = discord.Embed(description=f"🧹・**{len(deleted)}** messages supprimés.",
                           color=0xFF5A5A, timestamp=datetime.now(UTC))
        em.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=em, ephemeral=True)

        with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
            logs_id = conn.execute("SELECT id FROM logs_channels WHERE name = 'clear'").fetchone()[0]
        logs_clear = self.bot.get_channel(logs_id) or await self.bot.fetch_channel(logs_id)
        em2 = discord.Embed(
            title="🧹・Nouveau clear",
            description=f"**{len(deleted)}** messages supprimés sur le serveur **{guild.name}** ({guild.id}).",
            color=0xFF5A5A, timestamp=datetime.now(UTC),
        )
        em2.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url,
                       url=interaction.user.display_avatar.url)
        em2.add_field(name="**Channel : **", value=f"ID : {channel.id} | Name : {channel.name} ({channel.mention})",
                      inline=False)
        em2.set_footer(text=f"Author ID : {interaction.user.id} | Name : {interaction.user.name}.")
        if isinstance(logs_clear, (discord.TextChannel, discord.Thread)):
            await logs_clear.send(embed=em2)

    @mod.command(name="timeout", description=localized(
        "To timeout a user for X seconds. If you think he/ she needs to rest.",
        "Pour exclure temporairement un membre pendant X secondes.",
    ))
    @app_commands.rename(user=localized("user", "membre"), duration=localized("duration", "durée"),
                         reason=localized("reason", "raison"))
    @app_commands.describe(
        user=localized("User to timeout.", "Membre à timeout."),
        duration=localized("Duration (in seconds).", "Durée (en secondes)."),
        reason=localized("Reason of the timeout.", "Raison de l'exclusion temporaire."),
    )
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: int,
                      reason: str = "Aucune raison"):
        if not await database_ready(interaction) or not await has_permission(interaction, "staff_role"):
            return
        guild = interaction.guild
        if guild is None:
            return
        await user.timeout(datetime.now(UTC) + timedelta(seconds=duration), reason=reason)
        await interaction.response.send_message(
            f"{user.mention} a été exclu pendant **{time_to_readable(guild.id, duration)}** pour **{reason}**.",
            ephemeral=True,
        )
        with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
            logs_id = conn.execute("SELECT id FROM logs_channels WHERE name = 'timeout'").fetchone()[0]
        logs_timeout = self.bot.get_channel(logs_id) or await self.bot.fetch_channel(logs_id)
        em = discord.Embed(title="🟠・Nouvelle exclusion temporaire",
                           description=f"Un membre vient de se faire exclure temporairement de **{guild.name}**.",
                           color=0xFF5A5A, timestamp=datetime.now(UTC))
        em.add_field(name="__Staff :__", value=str(interaction.user), inline=True)
        em.add_field(name="__Membre :__", value=str(user), inline=True)
        em.add_field(name="__Durée de l'exclusion :__", value=time_to_readable(guild.id, duration), inline=True)
        em.add_field(name="__Raison :__", value=reason)
        em.set_footer(text=f"Staff ID : {interaction.user.id} | Member ID : {user.id}")
        if isinstance(logs_timeout, (discord.TextChannel, discord.Thread)):
            await logs_timeout.send(embed=em)

    @mod.command(name="untimeout", description=localized(
        "To untimeout a user.", "Pour annuler l'exclusion temporaire d'un membre.",
    ))
    @app_commands.rename(user=localized("user", "membre"), reason=localized("reason", "raison"))
    @app_commands.describe(user=localized("User to untimeout.", "Membre à untimeout."),
                           reason=localized("Reason of the untimeout.", "Raison de l'untimeout."))
    async def untimeout(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Aucune raison"):
        if not await database_ready(interaction) or not await has_permission(interaction, "staff_role"):
            return
        guild = interaction.guild
        if guild is None:
            return
        await user.timeout(None, reason=reason)
        await interaction.response.send_message(
            f"L'exclusion de {user.mention} a été annulé pour **{reason}**.", ephemeral=True,
        )
        with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
            logs_id = conn.execute("SELECT id FROM logs_channels WHERE name = 'timeout'").fetchone()[0]
        logs_untimeout = self.bot.get_channel(logs_id) or await self.bot.fetch_channel(logs_id)
        em = discord.Embed(title="🟢・Fin d'exclusion temporaire",
                           description=f"Un staff vient de retirer l'exclusion temporaire d'un membre sur **{guild.name}**.",
                           color=0x4CFF4C, timestamp=datetime.now(UTC))
        em.add_field(name="__Staff :__", value=str(interaction.user), inline=True)
        em.add_field(name="__Membre :__", value=str(user), inline=True)
        em.add_field(name="__Raison :__", value=reason)
        em.set_footer(text=f"Staff ID : {interaction.user.id} | Member ID : {user.id}")
        if isinstance(logs_untimeout, (discord.TextChannel, discord.Thread)):
            await logs_untimeout.send(embed=em)


async def setup(bot: commands.Bot):
    await install_translator(bot)
    await bot.add_cog(Mod(bot))
