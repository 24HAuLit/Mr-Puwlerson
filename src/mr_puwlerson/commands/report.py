import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.coinflip import enable_french_localizations


class Report(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="report", description="Report a problem with a channel.")
    @app_commands.guild_only()
    @app_commands.rename(
        channel=app_commands.locale_str("channel", fr="salon"),
        problem=app_commands.locale_str("problem", fr="probleme"),
        user=app_commands.locale_str("user", fr="utilisateur"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("Channel to look at", fr="Salon ou regarder"),
        problem=app_commands.locale_str("What's happening", fr="Quel est le problème"),
        user=app_commands.locale_str("Optional: a specific user to report", fr="Optionnel: un utilisateur spécifique à signaler"),
    )
    async def report(self, interaction: discord.Interaction, channel: discord.abc.GuildChannel,
                     problem: str, user: discord.User | None = None):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        path = Path(f"./Database/{guild.id}.db")
        if not path.exists():
            await interaction.response.send_message(
                f"Database not found for ID `{guild.id}`. This server is not configured yet.", ephemeral=True
            )
            return

        with sqlite3.connect(path) as conn:
            log_channel_id = conn.execute("SELECT id FROM logs_channels WHERE name = 'report'").fetchone()[0]
            conn.execute("INSERT INTO reports VALUES (?, ?, ?, ?)",
                         (interaction.user.id, user.id if user else None, channel.id, problem))

        await interaction.response.send_message("Reported the problem to the staff.", ephemeral=True)

        author = interaction.user
        author_name = author.name if author.discriminator == "0" else str(author)
        if user is not None:
            user_name = user.name if user.discriminator == "0" else str(user)
            description = f"**{author_name}** reported a problem with **{user_name}** in **{channel.name}**."
        else:
            description = f"**{author_name}** reported a problem in **{channel.name}**."

        em = discord.Embed(title="🔒・Report", description=description, color=0xFF0000,
                           timestamp=datetime.now(UTC))
        em.add_field(name="Problem", value=problem)
        log_channel = self.bot.get_channel(log_channel_id)
        if isinstance(log_channel, (discord.TextChannel, discord.Thread)):
            await log_channel.send(embed=em)
        else:
            await interaction.followup.send("The report was saved, but the report log channel is unavailable.", ephemeral=True)


async def setup(bot: commands.Bot):
    await enable_french_localizations(bot)
    await bot.add_cog(Report(bot))
