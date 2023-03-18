import os
import sqlite3
import interactions
from interactions import CommandContext, Embed
from datetime import datetime, timedelta
from message_config import ErrorMessage


def check_pinned(message):
    return not message.pinned


class Mod(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(dm_permission=False)
    async def mod(self, ctx):
        guild = await ctx.get_guild()

        if os.path.exists(f"./Database/{guild.id}.db") is False:
            return await ctx.send(ErrorMessage.database_not_found(guild.id), ephemeral=True)

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        if await ctx.author.has_permissions(interactions.Permissions.ALL):
            pass
        elif c.execute(f"SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0] in ctx.author.roles:
            pass
        else:
            await ctx.send(ErrorMessage.MissingPermissions(guild.id), ephemeral=True)
            return interactions.StopCommand()

        conn.close()

    @mod.subcommand()
    @interactions.option(
        description="Message to delete. Default : 5",
        required=False
    )
    async def clear(self, ctx: CommandContext, number: int = 5):
        """Delete X message(s) from chat."""
        guild = await ctx.get_guild()

        if os.path.exists(f"./Database/{guild.id}.db") is False:
            return

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        channel = ctx.channel
        await channel.purge(amount=number, check=check_pinned)

        em = Embed(
            description=f"🧹・**{number}** messages supprimés.",
            color=0xFF5A5A,
            timestamp=datetime.utcnow()
        )
        em.set_footer(icon_url=ctx.member.user.avatar_url,
                      text=f"Commande demandé par {ctx.author.name}#{ctx.author.discriminator}.")

        await ctx.send(embeds=em, ephemeral=True)

        logs_clear = await interactions.get(self.bot, interactions.Channel, object_id=
        c.execute("SELECT id FROM logs_channels WHERE name = 'clear'").fetchone()[0])

        conn.close()

        em2 = Embed(
            title="🧹・Nouveau clear",
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
    @interactions.option("User to timeout.")
    @interactions.option("Duration (in seconds).")
    @interactions.option(description="Reason.", required=False)
    async def timeout(self, ctx: interactions.CommandContext, user: interactions.User, duration: int,
                      reason: str = "Aucune raison"):
        """To timeout a user for X seconds. If you think he/ she needs to rest."""
        tempo = datetime.utcnow() + timedelta(seconds=duration)

        if duration < 60:
            duration = f"{duration} secondes"
        elif duration < 3600:
            if duration % 60 == 0:
                duration = f"{duration // 60} minutes"
            else:
                duration = f"{duration // 60} minutes et {duration % 60} secondes"
        elif duration < 86400:
            if duration % 3600 == 0:
                duration = f"{duration // 3600} heures"
            else:
                if duration % 60 == 0:
                    duration = f"{duration // 3600} heures et {duration % 3600 // 60} minutes"
                else:
                    duration = f"{duration // 3600} heures, {duration % 3600 // 60} minutes et {duration % 60} secondes"
        elif duration < 604800:
            if duration % 86400 == 0:
                duration = f"{duration // 86400} jours"
            else:
                if duration % 3600 == 0:
                    duration = f"{duration // 86400} jours et {duration % 86400 // 3600} heures"
                else:
                    if duration % 60 == 0:
                        duration = f"{duration // 86400} jours, {duration % 86400 // 3600} heures et {duration % 3600 // 60} minutes"
                    else:
                        duration = f"{duration // 86400} jours, {duration % 86400 // 3600} heures, {duration % 3600 // 60} minutes et {duration % 60} secondes"
        elif duration < 2592000:
            if duration % 604800 == 0:
                duration = f"{duration // 604800} semaines"
            else:
                if duration % 86400 == 0:
                    duration = f"{duration // 604800} semaines et {duration % 604800 // 86400} jours"
                else:
                    if duration % 3600 == 0:
                        duration = f"{duration // 604800} semaines, {duration % 604800 // 86400} jours et {duration % 86400 // 3600} heures"
                    else:
                        if duration % 60 == 0:
                            duration = f"{duration // 604800} semaines, {duration % 604800 // 86400} jours, {duration % 86400 // 3600} heures et {duration % 3600 // 60} minutes"
                        else:
                            duration = f"{duration // 604800} semaines, {duration % 604800 // 86400} jours, {duration % 86400 // 3600} heures, {duration % 3600 // 60} minutes et {duration % 60} secondes"

        guild = await ctx.get_guild()

        await user.modify(communication_disabled_until=tempo.isoformat(), guild_id=guild.id, reason=reason)
        await ctx.send(f"{user.mention} a été exclu pendant **{duration}** pour **{reason}**.", ephemeral=True)

        # Partie Logs
        if os.path.exists(f"./Database/{guild.id}.db") is False:
            return

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        logs_timeout = await interactions.get(self.bot, interactions.Channel, object_id=
        c.execute("SELECT id FROM logs_channels WHERE name = 'timeout'").fetchone()[0])

        conn.close()

        em = Embed(
            title="🟠・Nouvelle exclusion temporaire",
            description=f"Un membre vient de se faire exclure temporairement de **{guild.name}**.",
            color=0xFF5A5A,
            timestamp=datetime.utcnow()
        )
        em.add_field(name="__Staff :__", value=f"{ctx.author.username}#{ctx.author.discriminator}", inline=True)
        em.add_field(name="__Membre :__", value=f"{user.username}#{user.discriminator}", inline=True)
        em.add_field(name="__Durée de l'exclusion :__", value=f"{duration}", inline=True)
        em.add_field(name="__Raison :__", value=reason)
        em.set_footer(text=f"Staff ID : {ctx.author.id} | Member ID : {user.id}")

        await logs_timeout.send(embeds=em)

    @mod.subcommand()
    @interactions.option("User to untimeout.")
    @interactions.option("Reason", required=False)
    async def untimeout(self, ctx: interactions.CommandContext, user: interactions.User, reason: str = "Aucune raison"):
        """To cancel user's timeout."""
        guild = await ctx.get_guild()

        await user.modify(communication_disabled_until=None, guild_id=guild.id, reason=reason)
        await ctx.send(f"L'exclusion de {user.mention} a été annulé pour **{reason}**.", ephemeral=True)

        if os.path.exists(f"./Database/{guild.id}.db") is False:
            return

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        logs_untimeout = await interactions.get(self.bot, interactions.Channel, object_id=
        c.execute("SELECT id FROM logs_channels WHERE name = 'timeout'").fetchone()[0])

        conn.close()

        # Partie Logs

        em = Embed(
            title="🟢・Fin d'exclusion temporaire",
            description=f"Un staff vient de retirer l'exclusion temporaire d'un membre sur **{guild.name}**.",
            color=0x4CFF4C,
            timestamp=datetime.utcnow()
        )
        em.add_field(name="__Staff :__", value=f"{ctx.author.username}#{ctx.author.discriminator}", inline=True)
        em.add_field(name="__Membre :__", value=f"{user.username}#{user.discriminator}", inline=True)
        em.add_field(name="__Raison :__", value=reason)
        em.set_footer(text=f"Staff ID : {ctx.author.id} | Member ID : {user.id}")

        await logs_untimeout.send(embeds=em)


def setup(bot):
    Mod(bot)
