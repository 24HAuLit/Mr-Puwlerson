import sqlite3
from contextlib import closing

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.staff.setup._shared import database_path, require_owner


class SetupPages(discord.ui.View):
    def __init__(self, embeds: list[discord.Embed], user_id: int):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.user_id = user_id
        self.page = 0
        self.message: discord.InteractionMessage | None = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Cette pagination ne vous appartient pas.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, custom_id="previous")
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page - 1) % len(self.embeds)
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, custom_id="next")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page + 1) % len(self.embeds)
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    async def on_timeout(self):
        if self.message is not None:
            for child in self.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = True
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass


class SetupTranslator(app_commands.Translator):
    async def translate(self, string: app_commands.locale_str, locale: discord.Locale,
                        context: app_commands.TranslationContext) -> str | None:
        if locale is discord.Locale.french:
            return string.extras.get("fr")
        return None


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        if self.bot.tree.translator is None:
            await self.bot.tree.set_translator(SetupTranslator())

    @app_commands.command(
        name="setup",
        description=app_commands.locale_str("To setup the bot", fr="Pour configurer le bot"),
    )
    @app_commands.guild_only()
    async def setup(self, interaction: discord.Interaction):
        if not await require_owner(interaction):
            return
        guild = interaction.guild
        if guild is None:
            return
        with closing(sqlite3.connect(database_path(guild.id))) as conn:
            c = conn.cursor()
            def config(column: str):
                return c.execute(f"SELECT {column} FROM config").fetchone()[0]

            auto_role = {
                0: "Désactivé", 1: "Activé", 2: "Mode verification"
            }.get(config("auto_role"), "Erreur -> Contact @24h")
            page1 = discord.Embed(
                title="Voici la configuration actuelle du bot sur le serveur.", color=0x00FFC8
            )
            page1.add_field(name="Catégorie des tickets", value=f"<#{config('ticket_parent')}>")
            logs_id = config("logs_server")
            logs_guild = self.bot.get_guild(logs_id)
            page1.add_field(name="Serveur de logs", value=f"{logs_guild.name if logs_guild else 'Inconnu'} ({logs_id})")
            page1.add_field(name="Langue", value=str(config("locale")))
            page1.add_field(name="Nombre de tickets par utilisateur", value=str(config("ticket_limit")))
            for label, column, inline in (
                ("Rôle Défaut", "default_role", False),
                ("Rôle Staff", "staff_role", True),
                ("Rôle Admin", "admin_role", True),
                ("Rôle Owner", "owner_role", True),
            ):
                role_id = config(column)
                role = guild.get_role(role_id)
                page1.add_field(name=label, value=role.mention if role else f"<@&{role_id}>", inline=inline)

            page2 = discord.Embed(
                title="Voici la configuration actuelle des plugins sur le serveur.", color=0x00FFC8
            )
            page2.add_field(name="Auto-rôle", value=auto_role)
            for label, name in (("Giveaway", "giveaway"), ("Suggestion", "suggestion"), ("Report", "report")):
                status = c.execute("SELECT status FROM plugins WHERE name = ?", (name,)).fetchone()
                page2.add_field(name=label, value=str(status[0]) if status else "Inconnu")

        view = SetupPages([page1, page2], interaction.user.id)
        await interaction.response.send_message(embed=page1, view=view)
        view.message = await interaction.original_response()


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
