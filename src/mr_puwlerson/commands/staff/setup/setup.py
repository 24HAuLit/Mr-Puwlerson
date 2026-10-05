import sqlite3
from contextlib import closing

import discord
from discord import app_commands
from discord.ext import commands

from mr_puwlerson.commands.staff.setup._server import ServerTypeSelect
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
    setup = app_commands.Group(
        name="setup",
        description=app_commands.locale_str("To setup the bot", fr="Pour configurer le bot"),
        guild_only=True,
    )

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        if self.bot.tree.translator is None:
            await self.bot.tree.set_translator(SetupTranslator())

    @setup.command(name="server", description="Permet de configurer les différents types de serveur.")
    async def server(self, interaction: discord.Interaction):
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
        view.add_item(ServerTypeSelect(self.bot))
        await interaction.response.send_message(embed=page1, view=view)
        view.message = await interaction.original_response()

    @setup.command(name="roles", description="Permet de configurer les différents roles du serveur principal.")
    async def roles(self, interaction: discord.Interaction):
        if not await require_owner(interaction):
            return
        guild = interaction.guild
        if guild is None:
            return
        with closing(sqlite3.connect(database_path(guild.id))) as conn, conn:
            for role in guild.roles:
                row = conn.execute("SELECT 1 FROM roles WHERE id = ?", (role.id,)).fetchone()
                if row is None:
                    conn.execute("INSERT INTO roles (name, id, type) VALUES (?, ?, NULL)", (role.name, role.id))
                else:
                    conn.execute("UPDATE roles SET name = ? WHERE id = ?", (role.name, role.id))
        view = discord.ui.View()
        view.add_item(discord.ui.RoleSelect(custom_id="default_menu", placeholder="Choisissez un rôle"))
        await interaction.response.send_message("Quel role sera le role par default ?", view=view, ephemeral=True)

    @setup.command(name="channels", description="Permet de configurer les différents channels du serveur principal.")
    async def channels(self, interaction: discord.Interaction):
        if not await require_owner(interaction):
            return
        guild = interaction.guild
        if guild is None:
            return
        with closing(sqlite3.connect(database_path(guild.id))) as conn, conn:
            for channel in guild.channels:
                row = conn.execute("SELECT 1 FROM channels WHERE id = ?", (channel.id,)).fetchone()
                if row is None:
                    conn.execute("INSERT INTO channels (name, id, type, hidden) VALUES (?, ?, NULL, 0)",
                                 (channel.name, channel.id))
                else:
                    conn.execute("UPDATE channels SET name = ? WHERE id = ?", (channel.name, channel.id))
            row = conn.execute("SELECT 1 FROM channels WHERE id = ?", (guild.id,)).fetchone()
            if row is None:
                conn.execute("INSERT INTO channels (name, id, type, hidden) VALUES (?, ?, 'guild', 0)",
                             (guild.name, guild.id))
            else:
                conn.execute("UPDATE channels SET name = ?, type = 'guild' WHERE id = ?", (guild.name, guild.id))
        if not guild.channels:
            await interaction.response.send_message("Aucun salon à configurer.", ephemeral=True)
            return
        view = discord.ui.View()
        view.add_item(discord.ui.ChannelSelect(
            custom_id="banned_channels", placeholder="Sélectionnez les channels qui seront cachés dans les logs.",
            min_values=1, max_values=min(25, len(guild.channels)),
        ))
        await interaction.response.send_message(
            "Sélectionnez les channels qui seront cachés dans les logs.", view=view, ephemeral=True
        )

    @setup.command(name="tickets", description="Permet de configurer les salons nécessaires aux tickets.")
    async def tickets(self, interaction: discord.Interaction):
        if not await require_owner(interaction):
            return
        guild = interaction.guild
        if guild is None:
            return
        if not guild.categories:
            await interaction.response.send_message("Aucune catégorie disponible pour les tickets.", ephemeral=True)
            return
        view = discord.ui.View()
        view.add_item(discord.ui.ChannelSelect(
            custom_id="ticket_category", placeholder="Sélectionnez la catégorie des tickets.",
            channel_types=[discord.ChannelType.category],
        ))
        await interaction.response.send_message("Sélectionnez la catégorie des tickets.", view=view, ephemeral=True)

    @setup.command(name="max_ticket", description="Permet de fixer une limite de ticket ouvert par utilisateur.")
    @app_commands.describe(limit="Nombre de ticket maximum par utilisateur. (Par défaut 3)")
    async def max_ticket(self, interaction: discord.Interaction, limit: int):
        if not await require_owner(interaction):
            return
        if limit < 1:
            await interaction.response.send_message("La limite doit être supérieure à zéro.", ephemeral=True)
            return
        guild = interaction.guild
        if guild is None:
            return
        with closing(sqlite3.connect(database_path(guild.id))) as conn, conn:
            conn.execute("UPDATE config SET ticket_limit = ?", (limit,))
        await interaction.response.send_message(
            f"Le nombre de ticket maximum par utilisateur a été mis à jour et est désormais de **{limit}**.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
