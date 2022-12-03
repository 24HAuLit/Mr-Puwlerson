import interactions
from interactions import CommandContext, Embed
from datetime import datetime, timedelta
from const import DATA


class Mod(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    async def mod(self, ctx):
        if await ctx.author.has_permissions(interactions.Permissions.ALL):
            pass
        elif DATA["roles"]["Staff"] in ctx.author.roles:
            pass
        else:
            await ctx.send(":x: Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            return interactions.StopCommand()

    @mod.subcommand()
    @interactions.option(
        name="number",
        description="Nombre de message à supprimer. Par défaut : 5",
        type=interactions.OptionType.INTEGER,
        required=False
    )
    async def clear(self, ctx: CommandContext, number: int = 5):
        """Supprime X message(x) du chat."""

        channel = ctx.channel
        await channel.purge(amount=number)

        em = Embed(
            description=f"🧹 **{number}** messages supprimés.",
            color=0xFF5A5A,
            timestamp=datetime.utcnow()
        )
        em.set_footer(icon_url=ctx.member.user.avatar_url, text=f"Commande demandé par {ctx.author}.")

        await ctx.send(embeds=em, ephemeral=True)

        logs_clear = await interactions.get(self.bot, interactions.Channel, object_id=DATA["logs"]["clear"])

        em2 = Embed(
            title="🧹 Nouveau clear",
            description=f"**{number}** messages supprimés sur le serveur **{ctx.guild.name}** ({ctx.guild.id}).",
            color=0xFF5A5A,
            timestamp=datetime.utcnow()
        )
        em2.set_author(name=ctx.author.name, icon_url=ctx.member.user.avatar_url, url=ctx.member.user.avatar_url)
        em2.add_field(name="**Channel : **", value=f"ID : {channel.id} | Name : {channel.name} ({channel.mention})",
                      inline=False)
        em2.set_footer(text=f"Author ID : {ctx.author.id} | Name : {ctx.author.name}.")

        await logs_clear.send(embeds=em2)

    @mod.subcommand()
    @interactions.option(
        name="user",
        description="Utilisateur à exclure.",
        type=interactions.OptionType.USER,
        required=True
    )
    @interactions.option(
        name="duration",
        description="Temps de l'exclusion (en secondes).",
        type=interactions.OptionType.INTEGER,
        required=True
    )
    @interactions.option(
        name="reason",
        description="Raison de l'exclusion.",
        type=interactions.OptionType.STRING,
        required=False
    )
    async def timeout(self, ctx: interactions.CommandContext, user: interactions.User, duration: int, reason: str = "Aucune raison"):
        """Pour exclure temporairement un membre. Si vous pensez qu'il mérite une pause."""

        tempo = datetime.utcnow() + timedelta(seconds=duration)
        await user.modify(communication_disabled_until=tempo.isoformat(), guild_id=DATA["principal"]["guild"], reason=reason)
        await ctx.send(f"{user.mention} a été exclu pendant **{duration} secondes** pour **{reason}**.", ephemeral=True)

        # Partie Logs

        logs_timeout = await interactions.get(self.bot, interactions.Channel, object_id=DATA["logs"]["timeout"])
        guild = await ctx.get_guild()

        em = Embed(
            title="Nouvelle exclusion temporaire",
            description=f"Un membre vient de se faire exclure temporairement de **{guild}**.",
            color=0xFF5A5A,
            timestamp=datetime.utcnow()
        )
        em.add_field(name="__Staff :__", value=ctx.author.name, inline=True)
        em.add_field(name="__Membre :__", value=user.name, inline=True)
        em.add_field(name="__Durée de l'exclusion :__", value=f"{duration} secondes", inline=True)
        em.add_field(name="__Raison :__", value=reason)
        em.set_footer(text=f"Staff ID : {ctx.author.id} | Member ID : {user.id}")

        await logs_timeout.send(embeds=em)

    @mod.subcommand()
    @interactions.option("User to untimeout.")
    @interactions.option(
        name="reason",
        description="Raison pour retirer l'exclusion.",
        type=interactions.OptionType.STRING,
        required=False
    )
    async def untimeout(self, ctx: interactions.CommandContext, user: interactions.User, reason: str = "Aucune raison"):
        """Pour annuler l'exclusion temporaire d'un membre."""

        await user.modify(communication_disabled_until=None, guild_id=DATA["principal"]["guild"], reason=reason)
        await ctx.send(f"L'exclusion de {user.mention} a été annulé pour **{reason}**.", ephemeral=True)

        logs_untimeout = await interactions.get(self.bot, interactions.Channel, object_id=DATA["logs"]["timeout"])
        guild = await ctx.get_guild()

        # Partie Logs

        em = Embed(
            title="Fin d'exclusion temporaire",
            description=f"Un staff vient de retirer l'exclusion temporaire d'un membre sur **{guild}**.",
            color=0x4CFF4C,
            timestamp=datetime.utcnow()
        )
        em.add_field(name="__Staff :__", value=ctx.author.name, inline=True)
        em.add_field(name="__Membre :__", value=user.name, inline=True)
        em.add_field(name="__Raison :__", value=reason)
        em.set_footer(text=f"Staff ID : {ctx.author.id} | Member ID : {user.id}")

        await logs_untimeout.send(embeds=em)


def setup(bot):
    Mod(bot)
