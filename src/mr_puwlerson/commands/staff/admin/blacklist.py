import sqlite3
from datetime import UTC, datetime

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.staff.banned_channel import (
    database_ready,
    error_message,
    has_permission,
    install_translator,
    localized,
)


class Blacklist(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="blacklist", description="Blacklist a user from the bot.")
    @app_commands.guild_only()
    @app_commands.rename(user=localized("user", "membre"), reason=localized("reason", "raison"))
    @app_commands.describe(
        user=localized("User to blacklist", "Membre à blacklist"),
        reason=localized("Reason of the blacklist", "Raison du blacklist"),
    )
    async def blacklist(self, interaction: discord.Interaction, user: discord.User, reason: str):
        if not await database_ready(interaction) or not await has_permission(interaction, "admin_role"):
            return

        guild = interaction.guild
        if guild is None:
            return
        with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
            channel_id = conn.execute("SELECT id FROM logs_channels WHERE name = 'blacklist'").fetchone()[0]
            if conn.execute("SELECT user_id FROM blacklist WHERE user_id = ?", (user.id,)).fetchone():
                await interaction.response.send_message(error_message(guild.id, "blacklisted"), ephemeral=True)
                return
            cursor = conn.execute("INSERT INTO blacklist (user_id, reason) VALUES (?, ?)", (user.id, reason))
            blacklist_id = cursor.lastrowid

        await interaction.response.send_message(f"{user.mention} ({user.id}) a bien été blacklist.", ephemeral=True)
        channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
        em = discord.Embed(
            title="🔒・Blacklist",
            description=f"User **{user.name}** has been blacklisted by **{interaction.user.name}**.",
            color=0xFF0000, timestamp=datetime.now(UTC),
        )
        em.add_field(name="Reason", value=reason)
        em.add_field(name="Blacklist ID", value=str(blacklist_id))
        em.set_footer(text=f"Staff ID : {interaction.user.id} | User ID : {user.id}")
        if isinstance(channel, (discord.TextChannel, discord.Thread)):
            await channel.send(embed=em)

        em_dm = discord.Embed(
            title="🔒・Blacklist",
            description=f"You have got blacklisted by **{interaction.user.name}** for **{reason}**.\n"
                        "You will be unblacklisted if you are nice or after a certain time.",
            color=0xFF0000, timestamp=datetime.now(UTC),
        )
        em_dm.set_footer(icon_url=interaction.user.display_avatar.url,
                         text=f"Staff : {interaction.user.name} ({interaction.user.id}) | ID : {blacklist_id}")
        await user.send(embed=em_dm)


async def setup(bot: commands.Bot):
    await install_translator(bot)
    await bot.add_cog(Blacklist(bot))
