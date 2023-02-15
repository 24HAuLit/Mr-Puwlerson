import sqlite3

import interactions
from datetime import datetime
from const import DATA


class Help(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    async def help(self, ctx: interactions.CommandContext):
        """Pour avoir toutes les commandes à porter de main."""

        guild = await ctx.get_guild()
        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        if ctx.author.id == ctx.guild.owner_id or c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles:
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
                value="```• setup server\n• setup roles\n• setup channels\n```",
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
            em3 = interactions.Embed(
                title="📑 Liste des commandes",
                description="• help | **Permet de connaître toutes les commandes du serveur.**\n• ping | "
                            "**Pong!**\n• pileface | **Permet de lancer une pièce (Pile ou Face)**\n• suggest | "
                            f"**Pour pouvoir poster une suggestion dans <#{DATA['main']['suggestion']}>** ",
                color=0x00FFEE,
                timestamp=datetime.utcnow()
            )
            em3.set_footer(
                icon_url=ctx.member.user.avatar_url,
                text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
            )
            await ctx.send(embeds=em3, ephemeral=True)


def setup(bot):
    Help(bot)
