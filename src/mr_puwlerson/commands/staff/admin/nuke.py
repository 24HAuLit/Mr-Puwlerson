import asyncio
import sqlite3
from datetime import UTC, datetime

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.staff.banned_channel import (
    database_ready,
    has_permission,
    install_translator,
    localized,
)


class NukeView(discord.ui.View):
    def __init__(self, bot: commands.Bot, author_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Cette confirmation ne vous appartient pas.", ephemeral=True)
            return False
        return await database_ready(interaction) and await has_permission(interaction, "admin_role")

    @discord.ui.button(label="Confirmer", style=discord.ButtonStyle.danger, emoji="💥", custom_id="confirm")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        actual = interaction.channel
        guild = interaction.guild
        if guild is None or not isinstance(actual, discord.TextChannel):
            await interaction.response.send_message("Cette commande nécessite un salon textuel.", ephemeral=True)
            return
        new = await actual.clone()
        await interaction.response.edit_message(content="Vous avez confirmé la destruction de ce salon", view=None)
        self.stop()

        count = 5
        embed = discord.Embed(description=f"Ce salon va disparaitre dans **{count}** secondes.",
                              color=0xFF0000, timestamp=datetime.now(UTC))
        embed.set_footer(icon_url=interaction.user.display_avatar.url,
                         text=f"Commande demandé par {interaction.user.name}.")
        warning_message = await actual.send(embed=embed)
        for _ in range(5):
            embed.description = f"Ce salon va disparaitre dans **{count}** secondes."
            await warning_message.edit(embed=embed)
            count -= 1
            await asyncio.sleep(1)

        await actual.delete(reason="Nuked")
        with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
            conn.execute("UPDATE channels SET id = ? WHERE id = ?", (new.id, actual.id))
            logs_id = conn.execute("SELECT id FROM logs_channels WHERE name = 'nuke'").fetchone()[0]

        await new.send(embed=discord.Embed(description="Salon tout neuf, rien que pour vous.",
                                           color=0x75FF75, timestamp=datetime.now(UTC)))
        logs_nuke = self.bot.get_channel(logs_id) or await self.bot.fetch_channel(logs_id)
        em = discord.Embed(title="**💣 Nouveau nuke**", description="Un channel a été nuke.",
                           color=0xFF0000, timestamp=datetime.now(UTC))
        em.add_field(name="**Ancien channel : **", value=f"Nom : {actual.name} | ID : {actual.id}")
        em.add_field(name="**Nouveau channel : **", value=f"Nom : {new.name} ({new.mention}) | ID : {new.id}")
        em.set_footer(icon_url=interaction.user.display_avatar.url,
                      text=f"Author ID : {interaction.user.id} | Name : {interaction.user.name}.")
        if isinstance(logs_nuke, (discord.TextChannel, discord.Thread)):
            await logs_nuke.send(embed=em)

    @discord.ui.button(label="Refuser", style=discord.ButtonStyle.success, emoji="🤔", custom_id="refused")
    async def refused(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Vous avez annulé la destruction de ce salon.", view=None)
        self.stop()


class Nuke(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="nuke", description=localized(
        "Destroy the channel like Nuketown in Black Ops 1.",
        "Détruit le channel tah Nuketown sur Black Ops 1.",
    ))
    @app_commands.guild_only()
    async def nuke(self, interaction: discord.Interaction):
        if not await database_ready(interaction) or not await has_permission(interaction, "admin_role"):
            return
        await interaction.response.send_message(
            "Voulez-vous vraiment détruire ce salon ? **Cette action est irréversible.**",
            view=NukeView(self.bot, interaction.user.id), ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await install_translator(bot)
    await bot.add_cog(Nuke(bot))
