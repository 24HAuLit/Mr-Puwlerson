import sqlite3
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.staff.staff_helpers import (
    database_ready,
    error_message,
    has_permission,
    install_translator,
    localized,
)


class SelfRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="self_role", description=localized(
        "Add a self role to a message", "Ajoute un self role à un message",
    ))
    @app_commands.guild_only()
    @app_commands.describe(message_id=localized("Message ID", "ID du message"),
                           emoji="Emoji", role=localized("Role to add", "Role à ajouter"))
    async def self_role(self, interaction: discord.Interaction, message_id: str, emoji: str, role: discord.Role):
        if not await database_ready(interaction) or not await has_permission(interaction, "admin_role"):
            return
        try:
            message = await interaction.channel.fetch_message(int(message_id))
        except (ValueError, discord.NotFound):
            await interaction.response.send_message(
                error_message(interaction.guild.id, "message_not_found", message_id), ephemeral=True,
            )
            return

        await message.add_reaction(emoji)
        with sqlite3.connect(f"./Database/{interaction.guild.id}.db") as conn:
            conn.execute("INSERT INTO self_role (message_id, emoji, role_id) VALUES (?, ?, ?)",
                         (message.id, emoji, role.id))
        await interaction.response.send_message(
            f"L'émoji {emoji} a bien été ajouté au message `{message.id}` !", ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None or not Path(f"./Database/{payload.guild_id}.db").exists():
            return
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return
        member = payload.member or guild.get_member(payload.user_id)
        if member is None:
            member = await guild.fetch_member(payload.user_id)
        if member.bot:
            return
        with sqlite3.connect(f"./Database/{guild.id}.db") as conn:
            rows = conn.execute("SELECT emoji, role_id FROM self_role WHERE message_id = ?",
                                (payload.message_id,)).fetchall()
        for emoji, role_id in rows:
            if payload.emoji != discord.PartialEmoji.from_str(emoji):
                continue
            role = guild.get_role(role_id)
            if role is None:
                return
            channel = guild.get_channel(payload.channel_id) or await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction(payload.emoji, member)
            if role in member.roles:
                await member.remove_roles(role)
                await member.send(f"Le role **{role.name}** a bien été retiré sur le serveur **{guild.name}** !")
            else:
                await member.add_roles(role)
                await member.send(f"Le role **{role.name}** a bien été ajouté sur le serveur **{guild.name}** !")
            return


async def setup(bot: commands.Bot):
    await install_translator(bot)
    await bot.add_cog(SelfRole(bot))
