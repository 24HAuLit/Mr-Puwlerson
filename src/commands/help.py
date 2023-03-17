import os
import sqlite3
import interactions
from datetime import datetime
from message_config import ErrorMessage, HelpMessage
from const import commands_list


class Help(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(dm_permission=False)
    @interactions.option(
        name="command",
        description="La commande que vous voulez avoir plus d'informations.",
        type=interactions.OptionType.STRING,
        choices=[
            interactions.Choice(name=command, value=command)
            for command in commands_list
        ],
        required=False
    )
    async def help(self, ctx: interactions.CommandContext, command: str = None):
        """Pour avoir toutes les commandes à porter de main."""
        guild = await ctx.get_guild()

        if os.path.exists(f"./Database/{guild.id}.db") is False:
            return await ctx.send(ErrorMessage.database_not_found(guild.id), ephemeral=True)

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        if command == "ping":
            return await ctx.send(embeds=HelpMessage.ping(ctx, guild.id), ephemeral=True)

        elif command == "pileface":
            return await ctx.send(embeds=HelpMessage.pileface(ctx, guild.id), ephemeral=True)

        elif command == "suggest":
            return await ctx.send(embeds=HelpMessage.suggestions(ctx, guild.id), ephemeral=True)

        elif command == "mod clear":
            staff_id = c.execute("SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0]
            staff_name = await interactions.get(self.bot, interactions.Role, object_id=staff_id)
            return await ctx.send(embeds=HelpMessage.clear(ctx, staff_name.name, guild.id), ephemeral=True)

        elif command == "mod timeout":
            staff_id = c.execute("SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0]
            staff_name = await interactions.get(self.bot, interactions.Role, object_id=staff_id)
            return await ctx.send(embeds=HelpMessage.timeout(ctx, staff_name.name, guild.id), ephemeral=True)

        elif command == "mod untimemout":
            staff_id = c.execute("SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0]
            staff_name = await interactions.get(self.bot, interactions.Role, object_id=staff_id)
            return await ctx.send(embeds=HelpMessage.untimeout(ctx, staff_name.name, guild.id), ephemeral=True)

        elif command == "nuke":
            staff_id = c.execute("SELECT id FROM roles WHERE type = 'Admin'").fetchone()[0]
            staff_name = await interactions.get(self.bot, interactions.Role, object_id=staff_id)
            return await ctx.send(embeds=HelpMessage.nuke(ctx, staff_name.name, guild.id), ephemeral=True)

        elif command == "blacklist":
            staff_id = c.execute("SELECT id FROM roles WHERE type = 'Admin'").fetchone()[0]
            staff_name = await interactions.get(self.bot, interactions.Role, object_id=staff_id)
            return await ctx.send(embeds=HelpMessage.blacklist(ctx, staff_name.name, guild.id), ephemeral=True)

        elif command == "unblacklist":
            staff_id = c.execute("SELECT id FROM roles WHERE type = 'Admin'").fetchone()[0]
            staff_name = await interactions.get(self.bot, interactions.Role, object_id=staff_id)
            return await ctx.send(embeds=HelpMessage.unblacklist(ctx, staff_name.name, guild.id), ephemeral=True)

        elif command == "giveaway":
            staff_id = c.execute("SELECT id FROM roles WHERE type = 'Admin'").fetchone()[0]
            staff_name = await interactions.get(self.bot, interactions.Role, object_id=staff_id)
            return await ctx.send(embeds=HelpMessage.giveaway(ctx, staff_name.name, guild.id), ephemeral=True)

        if ctx.author.id == ctx.guild.owner_id or c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] \
                in ctx.author.roles:
            conn.close()

            em = interactions.Embed(
                title="📑 Liste des commandes",
                color=0x00FFEE,
                timestamp=datetime.utcnow()
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
                icon_url=ctx.member.user.avatar_url,
                text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
            )
            return await ctx.send(embeds=em, ephemeral=True)

        if c.execute("SELECT id FROM roles WHERE type = 'Admin'").fetchone()[0] in ctx.author.roles:
            conn.close()

            em1 = interactions.Embed(
                title="📑 Liste des commandes",
                color=0x00FFEE,
                timestamp=datetime.utcnow()
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
                icon_url=ctx.member.user.avatar_url,
                text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
            )
            return await ctx.send(embeds=em1, ephemeral=True)

        elif c.execute("SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0] in ctx.author.roles:
            conn.close()

            em2 = interactions.Embed(
                title="📑 Liste des commandes",
                color=0x00FFEE,
                timestamp=datetime.utcnow()
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
                icon_url=ctx.member.user.avatar_url,
                text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
            )
            return await ctx.send(embeds=em2, ephemeral=True)

        else:
            suggest = c.execute("SELECT id FROM channels WHERE type = 'suggest'").fetchone()[0]
            conn.close()

            em3 = interactions.Embed(
                title="📑 Liste des commandes",
                description="• help | **Permet de connaître toutes les commandes du serveur.**\n• ping | "
                            "**Pong!**\n• pileface | **Permet de lancer une pièce (Pile ou Face)**\n• suggest | "
                            f"**Pour pouvoir poster une suggestion dans <#{suggest}>** ",
                color=0x00FFEE,
                timestamp=datetime.utcnow()
            )
            em3.set_footer(
                icon_url=ctx.member.user.avatar_url,
                text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
            )

            return await ctx.send(embeds=em3, ephemeral=True)


def setup(bot):
    Help(bot)
