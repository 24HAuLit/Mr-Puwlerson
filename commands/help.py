import interactions
from datetime import datetime
from const import DATA


class Help(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    async def help(self, ctx: interactions.CommandContext):
        """Pour avoir toutes les commandes à porter de main."""

        if DATA["roles"]["Staff"] in ctx.author.roles or DATA["roles"]["Owner"] in ctx.author.roles:
            em = interactions.Embed(
                title="📑 Liste des commandes",
                color=0x00FFEE,
                timestamp=datetime.utcnow()
            )
            em.add_field(
                name="**Default**",
                value="```\n• help\n• ping\n• question\n• suggest\n```",
                inline=True
            )
            em.add_field(
                name="**Staff**",
                value="```\n• mod clear\n• mod timeout\n• mod untimemout\n• nuke (Admin only)\n• blacklist (Admin only)\n• unblacklist (Admin only)\n```",
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
            await ctx.send(embeds=em, ephemeral=True)

        else:
            em2 = interactions.Embed(
                title="📑 Liste des commandes",
                description="• help | **Permet de connaître toutes les commandes du serveur.**\n• ping | "
                            "**Pong!**\n• question | **Pour pouvoir poser une question à un staff *(Seulement en "
                            "MP)***\n• suggest | **Pour pouvoir poster une suggestion dans <#1011704888679477369>** ",
                color=0x00FFEE,
                timestamp=datetime.utcnow()
            )
            em2.set_footer(
                icon_url=ctx.member.user.avatar_url,
                text="Le bot utilise les slash-commands, donc il faut mettre un / a chaque début."
            )
            await ctx.send(embeds=em2, ephemeral=True)


def setup(bot):
    Help(bot)
