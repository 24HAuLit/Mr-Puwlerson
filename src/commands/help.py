import os
import sqlite3
import interactions
from interactions import LocalizedDesc
from src.utils.message_config import HelpMessage
from src.utils.checks import database_exists
from src.utils.const import commands_list


class Help(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.slash_command(
        description=LocalizedDesc(english_us="To have all the commands at hand.", french="Pour avoir toutes les "
                                                                                         "commandes à porter de main."),
    )
    @interactions.slash_option(
        name="command",
        description=LocalizedDesc(english_us="To get information on a command.", french="Pour avoir des informations "
                                                                                        "sur une commande."),
        opt_type=interactions.OptionType.STRING,
        choices=[
            interactions.SlashCommandChoice(name=command, value=command)
            for command in commands_list
        ],
        required=False
    )
    async def help(self, ctx: interactions.SlashContext, command: str = None):
        guild = ctx.guild

        if await database_exists(ctx) is not True:
            return

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        if command == "ping":
            return await ctx.send(embeds=HelpMessage.ping(ctx, guild.id), ephemeral=True)

        elif command == "pileface":
            return await ctx.send(embeds=HelpMessage.pileface(ctx, guild.id), ephemeral=True)

        elif command == "suggest":
            return await ctx.send(embeds=HelpMessage.suggestions(ctx, guild.id), ephemeral=True)

        elif command == "mod clear":
            staff_role_id = c.execute("SELECT staff_role FROM config").fetchone()[0]
            staff_role = guild.get_role(staff_role_id)
            return await ctx.send(embeds=HelpMessage.clear(ctx, staff_role.name, guild.id), ephemeral=True)

        elif command == "mod timeout":
            staff_role_id = c.execute("SELECT staff_role FROM config").fetchone()[0]
            staff_role = guild.get_role(staff_role_id)
            return await ctx.send(embeds=HelpMessage.timeout(ctx, staff_role.name, guild.id), ephemeral=True)

        elif command == "mod untimemout":
            staff_role_id = c.execute("SELECT staff_role FROM config").fetchone()[0]
            staff_role = guild.get_role(staff_role_id)
            return await ctx.send(embeds=HelpMessage.untimeout(ctx, staff_role.name, guild.id), ephemeral=True)

        elif command == "nuke":
            staff_role_id = c.execute("SELECT admin_role FROM config").fetchone()[0]
            staff_role = guild.get_role(staff_role_id)
            return await ctx.send(embeds=HelpMessage.nuke(ctx, staff_role.name, guild.id), ephemeral=True)

        elif command == "blacklist":
            staff_role_id = c.execute("SELECT admin_role FROM config").fetchone()[0]
            staff_role = guild.get_role(staff_role_id)
            return await ctx.send(embeds=HelpMessage.blacklist(ctx, staff_role.name, guild.id), ephemeral=True)

        elif command == "unblacklist":
            staff_role_id = c.execute("SELECT admin_role FROM config").fetchone()[0]
            staff_role = guild.get_role(staff_role_id)
            return await ctx.send(embeds=HelpMessage.unblacklist(ctx, staff_role.name, guild.id), ephemeral=True)

        elif command == "giveaway":
            staff_role_id = c.execute("SELECT admin_role FROM config").fetchone()[0]
            staff_role = guild.get_role(staff_role_id)
            return await ctx.send(embeds=HelpMessage.giveaway(ctx, staff_role.name, guild.id), ephemeral=True)

        elif command == "setup server":
            staff_role_id = c.execute("SELECT owner_role FROM config").fetchone()[0]
            staff_role = guild.get_role(staff_role_id)
            return await ctx.send(embeds=HelpMessage.setup_server(ctx, staff_role.name, guild.id), ephemeral=True)

        if ctx.guild.is_owner(ctx.author.id) or c.execute("SELECT owner_role FROM config").fetchone()[0] \
                in ctx.author.roles:
            conn.close()

            em = interactions.Embed(
                title="📑 Liste des commandes",
                color=0x00FFEE,
                timestamp=interactions.Timestamp.utcnow()
            )
            em.add_field(
                name="**Default**",
                value="```\n• help\n• ping\n• pileface\n• suggest\n```",
                inline=True
            )
            em.add_field(
                name="**Staff**",
                value="```\n• mod clear\n• mod timeout\n• mod untimemout\n```",
                inline=True
            )
            em.add_field(
                name="**Admin**",
                value="```\n• nuke\n• blacklist\n• unblacklist\n• Giveaway\n```",
                inline=True
            )
            em.add_field(
                name="**Owner**",
                value="```• setup server\n• setup roles\n• setup channels\n• setup tickets\n• setup max_ticket\n• locale\n• update```",
                inline=True
            )
            em.add_field(
                name="**Ticket**",
                value="```\n• add\n• remove\n• rename\n• close\n• close_reason\n```",
                inline=True
            )
            em.set_footer(
                icon_url=ctx.member.avatar.url,
                text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
            )
            return await ctx.send(embeds=em, ephemeral=True)

        if c.execute("SELECT admin_role FROM config").fetchone()[0] in ctx.author.roles:
            conn.close()

            em1 = interactions.Embed(
                title="📑 Liste des commandes",
                color=0x00FFEE,
                timestamp=interactions.Timestamp.utcnow()
            )
            em1.add_field(
                name="**Default**",
                value="```\n• help\n• ping\n• pileface\n• suggest\n```",
                inline=True
            )
            em1.add_field(
                name="**Staff**",
                value="```\n• mod clear\n• mod timeout\n• mod untimemout\n```",
                inline=True
            )
            em1.add_field(
                name="**Admin**",
                value="```\n• nuke\n• blacklist\n• unblacklist\n• Giveaway\n```",
                inline=True
            )
            em1.add_field(
                name="**Ticket**",
                value="```\n• add\n• remove\n• rename\n• close\n• close_reason\n```",
                inline=True
            )
            em1.set_footer(
                icon_url=ctx.member.avatar.url,
                text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
            )
            return await ctx.send(embeds=em1, ephemeral=True)

        elif c.execute("SELECT staff_role FROM config").fetchone()[0] in ctx.author.roles:
            conn.close()

            em2 = interactions.Embed(
                title="📑 Liste des commandes",
                color=0x00FFEE,
                timestamp=interactions.Timestamp.utcnow()
            )
            em2.add_field(
                name="**Default**",
                value="```\n• help\n• ping\n• pileface\n• suggest\n```",
                inline=True
            )
            em2.add_field(
                name="**Staff**",
                value="```\n• mod clear\n• mod timeout\n• mod untimemout\n```",
                inline=True
            )
            em2.add_field(
                name="**Ticket**",
                value="```\n• add\n• remove\n• rename\n• close\n• close_reason\n```",
                inline=True
            )
            em2.set_footer(
                icon_url=ctx.member.avatar.url,
                text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
            )
            return await ctx.send(embeds=em2, ephemeral=True)

        else:
            suggest = c.execute("SELECT suggest_channel FROM config").fetchone()[0]
            conn.close()

            em3 = interactions.Embed(
                title="📑 Liste des commandes",
                description="• help | **Permet de connaître toutes les commandes du serveur.**\n• ping | "
                            "**Pong!**\n• pileface | **Permet de lancer une pièce (Pile ou Face)**\n• suggest | "
                            f"**Pour pouvoir poster une suggestion dans <#{suggest}>** ",
                color=0x00FFEE,
                timestamp=interactions.Timestamp.utcnow()
            )
            em3.set_footer(
                icon_url=ctx.member.user.avatar.url,
                text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
            )

            return await ctx.send(embeds=em3, ephemeral=True)

