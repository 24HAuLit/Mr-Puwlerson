import asyncio
import random
import sqlite3
from time import time

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.staff.staff_helpers import (
    database_ready,
    error_message,
    has_permission,
    install_translator,
    localized,
    plugin_ready,
)
from mr_puwlerson.utils.time_converter import readable_to_time


class GiveawayView(discord.ui.View):
    def __init__(self, participants: set[int]):
        super().__init__(timeout=None)
        self.participants = participants

    @discord.ui.button(label="Participer", style=discord.ButtonStyle.success, custom_id="giveaway")
    async def participate(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        if guild is None or not isinstance(member, discord.Member):
            return
        with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
            owner_role, admin_role = conn.execute("SELECT owner_role, admin_role FROM config").fetchone()
        role_ids = {role.id for role in member.roles}
        if owner_role in role_ids or admin_role in role_ids:
            await interaction.response.send_message("Vous ne pouvez pas participer au giveaway !", ephemeral=True)
        elif interaction.user.id not in self.participants:
            self.participants.add(interaction.user.id)
            await interaction.response.send_message("Vous participez désormais au giveaway !", ephemeral=True)
        else:
            self.participants.remove(interaction.user.id)
            await interaction.response.send_message("Vous ne participez plus au giveaway !", ephemeral=True)


class Giveaway(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active = False
        self.participants: set[int] = set()
        self.task: asyncio.Task | None = None

    @app_commands.command(name="giveaway", description=localized("Start a giveaway", "Lance un giveaway"))
    @app_commands.guild_only()
    @app_commands.rename(
        prize=localized("prize", "gain"), duration=localized("duration", "durée"),
        winners=localized("winners", "gagnants"),
    )
    @app_commands.describe(
        prize=localized("What is the prize ?", "Quel est le gain ?"),
        duration=localized("How long will the giveaway last ?", "Combien de temps va durer le giveaway ?"),
        winners=localized("How many winners ? (Default : 1)", "Combien de gagnants ? (Par défaut : 1)"),
    )
    async def giveaway(self, interaction: discord.Interaction, prize: str, duration: str, winners: int = 1):
        if not await database_ready(interaction) or not await has_permission(interaction, "admin_role"):
            return
        if not await plugin_ready(interaction, "giveaway"):
            return
        guild = interaction.guild
        if guild is None:
            return
        if self.active:
            await interaction.response.send_message(error_message(guild.id, "giveaway_started"), ephemeral=True)
            return
        try:
            time_to_wait = readable_to_time(duration[:-1], duration[-1])
            if not isinstance(time_to_wait, int) or time_to_wait <= 0 or winners < 1:
                raise ValueError
        except (ValueError, IndexError, TypeError):
            await interaction.response.send_message("Durée ou nombre de gagnants invalide.", ephemeral=True)
            return

        with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
            row = conn.execute("SELECT id FROM channels WHERE lower(type) = 'giveaway'").fetchone()
            logs_row = conn.execute("SELECT id FROM logs_channels WHERE name = 'giveaway'").fetchone()
        if row is None:
            await interaction.response.send_message("Le salon des giveaways n'est pas configuré.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        channel = self.bot.get_channel(row[0]) or await self.bot.fetch_channel(row[0])
        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            await interaction.followup.send("Le salon des giveaways n'est pas configuré.", ephemeral=True)
            return
        self.active = True
        self.participants.clear()
        view = GiveawayView(self.participants)
        em = discord.Embed(
            title="Nouveau Giveaway ! 🎊",
            description=f"Un giveaway a été lancé par {interaction.user.mention} !\n*Cliquez sur le bouton ci-dessous pour participer.*",
            color=0x00FFC8,
        )
        em.add_field(name="Gain", value=prize)
        em.add_field(name="Nombre de gagnants", value=str(winners))
        em.add_field(name="Date de fin", value=f"<t:{int(time() + time_to_wait)}:R>")
        try:
            message = await channel.send(embed=em, view=view)
        except Exception:
            self.active = False
            raise
        await interaction.followup.send("Le giveaway a bien été lancé !", ephemeral=True)
        self.task = asyncio.create_task(
            self.finish(message, channel, logs_row[0] if logs_row else None,
                        interaction.user.mention, prize, winners, time_to_wait, view)
        )

    async def finish(self, message: discord.Message, channel, logs_id: int | None,
                     author_mention: str, prize: str, winners: int, delay: int, view: GiveawayView):
        try:
            await asyncio.sleep(delay)
            selected = random.sample(list(self.participants), min(winners, len(self.participants)))
            mentions = [f"<@{user_id}>" for user_id in selected]
            winner_text = ", ".join(mentions) if mentions else "Aucun participant"
            em_end = discord.Embed(
                title="Nouveau Giveaway ! 🎊",
                description=f"Le giveaway lancé par {author_mention} est terminé ! ",
                color=0x75FD75,
            )
            em_end.add_field(name="Gain", value=prize, inline=True)
            em_end.add_field(name="Gagnant", value=winner_text, inline=True)
            em_end.add_field(name="Nombre de participants", value=str(len(self.participants)), inline=True)
            view.stop()
            await message.edit(embed=em_end, view=None)
            if not mentions:
                await channel.send("Le giveaway est terminé ! Aucun participant.")
            elif winners == 1:
                await channel.send(f"Le giveaway est terminé ! Le gagnant est {winner_text} !")
            else:
                await channel.send(f"Le giveaway est terminé ! Les gagnants sont {winner_text} !")
            if logs_id is not None:
                logs = self.bot.get_channel(logs_id) or await self.bot.fetch_channel(logs_id)
                if not isinstance(logs, (discord.TextChannel, discord.Thread)):
                    return
                em = discord.Embed(title="🎊・Giveaway", description=f"Le giveaway lancé par {author_mention} est terminé !",
                                   color=0x75FD75)
                em.add_field(name="Gain", value=prize, inline=True)
                em.add_field(name="Gagnant", value=winner_text, inline=True)
                em.add_field(name="Nombre de participants", value=str(len(self.participants)), inline=True)
                await logs.send(embed=em)
        finally:
            view.stop()
            self.participants.clear()
            self.active = False
            self.task = None

    async def cog_unload(self):
        if self.task is not None:
            self.task.cancel()


async def setup(bot: commands.Bot):
    await install_translator(bot)
    await bot.add_cog(Giveaway(bot))
