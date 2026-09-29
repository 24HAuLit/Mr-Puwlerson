import sqlite3
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.staff.banned_channel import (
    database_ready,
    has_permission,
    install_translator,
    localized,
)


class UnBlacklist(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="unblacklist", description=localized("Unblacklist a member", "Unblacklist un membre"))
    @app_commands.guild_only()
    @app_commands.rename(user=localized("user", "membre"), reason=localized("reason", "raison"))
    @app_commands.describe(
        user=localized("User to unblacklist", "Membre à unblacklist"),
        reason=localized("Reason of the unblacklist", "Raison du unblacklist"),
    )
    async def unblacklist(self, interaction: discord.Interaction, user: discord.User, reason: str = "Aucune raison"):
        if not await database_ready(interaction) or not await has_permission(interaction, "admin_role"):
            return

        guild = interaction.guild
        with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
            channel_id = conn.execute("SELECT id FROM logs_channels WHERE name = 'blacklist'").fetchone()[0]
            row = conn.execute("SELECT blacklist_id FROM blacklist WHERE user_id = ?", (user.id,)).fetchone()
            if row is None:
                await interaction.response.send_message(
                    "Sorry, but you can't unblacklist someone who is not blacklist.", ephemeral=True
                )
                return
            blacklist_id = row[0]
            conn.execute("DELETE FROM blacklist WHERE user_id = ?", (user.id,))

        await interaction.response.send_message(f"{user.mention} ({user.id}) is no longer blacklisted.", ephemeral=True)
        channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
        em = discord.Embed(
            title="🔓・Unblacklist",
            description=f"User **{user.name}** has been unblacklisted by **{interaction.user.name}**",
            color=0x00FF00, timestamp=datetime.now(timezone.utc),
        )
        em.add_field(name="Reason", value=reason)
        em.add_field(name="Blacklist ID", value=str(blacklist_id))
        em.set_footer(text=f"Staff ID : {interaction.user.id} | User ID : {user.id}")
        await channel.send(embed=em)

        em_dm = discord.Embed(
            title="🔓・Unblacklist",
            description=f"Vous have been unblacklisted by **{interaction.user.name}** for **{reason}**.\n"
                        "You had been nice, it's good, now continue on this path.",
            color=0x00FF00, timestamp=datetime.now(timezone.utc),
        )
        em_dm.set_footer(icon_url=interaction.user.display_avatar.url,
                         text=f"Staff : {interaction.user.name} ({interaction.user.id}) | ID : {blacklist_id}")
        await user.send(embed=em_dm)


async def setup(bot: commands.Bot):
    await install_translator(bot)
    await bot.add_cog(UnBlacklist(bot))
