import sqlite3
import interactions
from interactions import Button, ButtonStyle
from interactions.ext import paginators
from interactions import LocalizedDesc
from src.utils.checks import database_exists, is_owner


class Setup(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.embeds = []

    @interactions.slash_command(
        description=LocalizedDesc(english_us="To setup the bot", french="Pour configurer le bot"),
        dm_permission=False
    )
    async def setup(self, ctx: interactions.SlashContext):
        if await database_exists(ctx) is not True:
            return
        if await is_owner(ctx) is not True:
            return

        conn = sqlite3.connect(f'./Database/{ctx.guild.id}.db')
        c = conn.cursor()

        buttons = buttons = [
            Button(style=ButtonStyle.PRIMARY, label="Previous", custom_id="previous"),
            Button(style=ButtonStyle.PRIMARY, label="Next", custom_id="next")
        ]

        if c.execute("SELECT auto_role FROM config").fetchone()[0] == 0:
            auto_role = "Désactivé"
        elif c.execute("SELECT auto_role FROM config").fetchone()[0] == 1:
            auto_role = "Activé"
        elif c.execute("SELECT auto_role FROM config").fetchone()[0] == 2:
            auto_role = "Mode verification"
        else:
            auto_role = "Erreur -> Contact @24h"

        page1 = interactions.Embed(
            title="Voici la configuration actuelle du bot sur le serveur.",
            color=0x00FFC8
        )
        page1.add_field(
            name="Catégorie des tickets",
            value=f"<#{c.execute('SELECT ticket_parent FROM config').fetchone()[0]}>",
            inline=True
        )
        page1.add_field(
            name="Serveur de logs",
            value=f"{self.bot.get_guild(c.execute('SELECT logs_server FROM config').fetchone()[0]).name} ({c.execute('SELECT logs_server FROM config').fetchone()[0]})",
        )
        page1.add_field(
            name="Langue",
            value=c.execute("SELECT locale FROM config").fetchone()[0],
            inline=True
        )
        page1.add_field(
            name="Nombre de tickets par utilisateur",
            value=c.execute("SELECT ticket_count FROM config").fetchone()[0],
            inline=True
        )
        page1.add_field(
            name="Rôle Défaut",
            value=self.bot.get_guild(ctx.guild_id).get_role(c.execute("SELECT default_role FROM config").fetchone()[0]).mention,
            inline=False
        )
        page1.add_field(
            name="Rôle Staff",
            value=self.bot.get_guild(ctx.guild_id).get_role(c.execute("SELECT staff_role FROM config").fetchone()[0]).mention,
            inline=True
        )
        page1.add_field(
            name="Rôle Admin",
            value=self.bot.get_guild(ctx.guild_id).get_role(c.execute("SELECT admin_role FROM config").fetchone()[0]).mention,
            inline=True
        )
        page1.add_field(
            name="Rôle Owner",
            value=self.bot.get_guild(ctx.guild_id).get_role(c.execute("SELECT owner_role FROM config").fetchone()[0]).mention,
            inline=True
        )

        page2 = interactions.Embed(
            title="Voici la configuration actuelle des plugins sur le serveur.",
            color=0x00FFC8
        )
        page2.add_field(
            name="Auto-rôle",
            value=auto_role,
            inline=True
        )
        page2.add_field(
            name="Giveaway",
            value=c.execute("SELECT status FROM plugins WHERE name = 'giveaway'").fetchone()[0],
            inline=True
        )
        page2.add_field(
            name="Suggestion",
            value=c.execute("SELECT status FROM plugins WHERE name = 'suggestion'").fetchone()[0],
            inline=True
        )
        page2.add_field(
            name="Report",
            value=c.execute("SELECT status FROM plugins WHERE name = 'report'").fetchone()[0],
            inline=True
        )

        self.embeds.append(page1)
        self.embeds.append(page2)

        conn.close()

        for embed in self.embeds:
            if not isinstance(embed, interactions.Embed):
                print("Found a non-embed object in the list.")

        paginator = paginators.Paginator.create_from_embeds(self.bot, self.embeds, timeout=60)
        await paginator.send(ctx)


def setup(bot):
    Setup(bot)
