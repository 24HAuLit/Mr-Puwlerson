import asyncio
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.coinflip import enable_french_localizations
from mr_puwlerson.utils.const import DATA
from mr_puwlerson.utils.time_converter import time_to_readable


def author_name(user: discord.User | discord.Member) -> str:
    return user.name if user.discriminator == "0" else str(user)


class SuggestionReason(discord.ui.Modal):
    reason = discord.ui.TextInput(label="Raison", placeholder="Pour quelle raison ?",
                                  style=discord.TextStyle.paragraph, max_length=100)

    def __init__(self, accepted: bool):
        self.accepted = accepted
        super().__init__(title="Raison", custom_id="accept_reason" if accepted else "refuse_reason")
        self.reason.placeholder = ("Pour quelle raison avez-vous accepté ?" if accepted
                                   else "Pour quelle raison avez-vous refusé ?")
        self.reason.custom_id = "acc_short_response" if accepted else "deny_short_response"

    async def on_submit(self, interaction: discord.Interaction):
        message = interaction.message
        if message is None or not message.embeds:
            await interaction.response.send_message("The suggestion message is unavailable.", ephemeral=True)
            return
        original = message.embeds[0]
        accepted = self.accepted
        label = "accepté" if accepted else "refusé"
        color = 0x00FF00 if accepted else 0xFF3C3C
        result = interaction.client.get_channel(DATA["main"]["suggest_result"])

        em = discord.Embed(title=f"Suggestion {label}", url=message.jump_url, color=color,
                           timestamp=datetime.now(UTC))
        em.add_field(name="__**Suggestion : **__", value=original.description, inline=False)
        em.add_field(name="__**Raison : **__", value=str(self.reason), inline=False)
        em.set_footer(icon_url=interaction.user.display_avatar.url,
                      text=f"Suggestion {label} par {author_name(interaction.user)}.")

        updated = discord.Embed(title=original.title, description=original.description,
                                color=color, timestamp=original.timestamp)
        updated.set_footer(icon_url=original.footer.icon_url, text=original.footer.text)
        await message.edit(embed=updated, view=None)
        await interaction.response.send_message(
            "Vous avez accepté la suggestion." if accepted else "Vous avez refusé cette suggestion.",
            ephemeral=True,
        )
        if isinstance(result, (discord.TextChannel, discord.Thread)):
            await result.send(embed=em)
        else:
            await interaction.followup.send("The result channel is unavailable.", ephemeral=True)


class SuggestionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def handle(self, interaction: discord.Interaction, accepted: bool):
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
            owner_role = conn.execute("SELECT owner_role FROM config").fetchone()[0]
            admin_role = conn.execute("SELECT admin_role FROM config").fetchone()[0]
            locale = conn.execute("SELECT locale FROM config").fetchone()[0]
        member = interaction.user
        if not isinstance(member, discord.Member):
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        if member.id != guild.owner_id and not any(role.id in (owner_role, admin_role) for role in member.roles):
            await interaction.response.send_message(
                ":x: Vous n'avez pas la permission de faire ceci." if locale == "fr"
                else ":x: You don't have the permission to do this.", ephemeral=True
            )
            return
        await interaction.response.send_modal(SuggestionReason(accepted))

    @discord.ui.button(label="Accepter", style=discord.ButtonStyle.success, custom_id="accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle(interaction, True)

    @discord.ui.button(label="Refuser", style=discord.ButtonStyle.danger, custom_id="refuse")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle(interaction, False)


class Suggestion(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.counter = 0

    async def cog_load(self):
        self.bot.add_view(SuggestionView())

    @app_commands.command(
        name="suggest",
        description=app_commands.locale_str("To be able to propose a suggestion.",
                                            fr="Pour pouvoir proposer une suggestion."),
    )
    @app_commands.guild_only()
    @app_commands.describe(suggestion=app_commands.locale_str("Your suggestion.", fr="Votre suggestion."))
    async def suggest(self, interaction: discord.Interaction, suggestion: str):
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
            c = conn.cursor()
            if c.execute("SELECT status FROM plugins WHERE name = ?", ("suggestion",)).fetchone()[0] != "true":
                locale = c.execute("SELECT locale FROM config").fetchone()[0]
                message = (":x: Désolé, mais le plugin `suggestion` est désactivé sur ce serveur."
                           if locale == "fr" else ":x: Sorry, but the plugin `suggestion` is disabled on this server.")
                await interaction.response.send_message(message, ephemeral=True)
                return

            if c.execute("SELECT 1 FROM blacklist WHERE user_id = ?", (interaction.user.id,)).fetchone():
                locale = c.execute("SELECT locale FROM config").fetchone()[0]
                message = (":x: Désolé, mais vous êtes blacklist. Vous ne pouvez donc pas effectuer cette action."
                           if locale == "fr" else ":x: Sorry, but you are blacklist. You cannot do this action.")
                await interaction.response.send_message(message, ephemeral=True)
                return

            row = c.execute("SELECT timestamp FROM cooldown WHERE user = ?", (interaction.user.id,)).fetchone()
            if row is None:
                c.execute("INSERT INTO cooldown VALUES (?, ?)", (interaction.user.id, 0))
                conn.commit()
                row = (0,)
            now = int(datetime.now(UTC).timestamp())
            if row[0] >= now:
                remaining = row[0] - now
                locale = c.execute("SELECT locale FROM config").fetchone()[0]
                duration = time_to_readable(guild.id, remaining)
                message = (f":x: Vous êtes en cooldown. Veuillez patienter encore {duration}." if locale == "fr"
                           else f":x: You are in cooldown. Please wait {duration}.")
                await interaction.response.send_message(message, ephemeral=True)
                return

            cooldown = c.execute("SELECT suggestion_cooldown FROM config").fetchone()[0]
            c.execute("UPDATE cooldown SET timestamp = ? WHERE user = ?", (now + cooldown, interaction.user.id))
            channel_id = c.execute("SELECT suggest_channel FROM config").fetchone()[0]

        channel = self.bot.get_channel(channel_id)
        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            await interaction.response.send_message("The suggestion channel is unavailable.", ephemeral=True)
            return
        self.counter += 1
        em = discord.Embed(title=f"Nouvelle suggestion #{self.counter}", description=suggestion,
                           color=0xFFF000, timestamp=datetime.now(UTC))
        em.set_footer(icon_url=interaction.user.display_avatar.url,
                      text=f"Suggestion proposé par {author_name(interaction.user)}.")
        await interaction.response.send_message(
            f"Votre suggestion a bien été posté dans {channel.mention}", ephemeral=True
        )
        message = await channel.send(embed=em, view=SuggestionView())
        await message.add_reaction("⬆️")
        await asyncio.sleep(1)
        await message.add_reaction("⬇️")


async def setup(bot: commands.Bot):
    await enable_french_localizations(bot)
    await bot.add_cog(Suggestion(bot))
