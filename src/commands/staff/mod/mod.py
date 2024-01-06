import io
import os
import sqlite3
import interactions
from interactions import SlashContext, Embed, LocalizedName, LocalizedDesc
from datetime import timedelta
from src.utils.message_config import ErrorMessage
from src.utils.time_converter import time_to_readable


def check_pinned(message):
    return not message.pinned


class Mod(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.slash_command(dm_permission=False)
    async def mod(self, ctx: SlashContext):
        guild = ctx.guild

        if os.path.exists(f"./Database/{guild.id}.db") is False:
            return await ctx.send(ErrorMessage.database_not_found(guild.id), ephemeral=True)

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        if ctx.author.has_permission(interactions.Permissions.ALL):
            pass
        elif c.execute(f"SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0] in ctx.author.roles:
            pass
        else:
            await ctx.send(ErrorMessage.MissingPermissions(guild.id), ephemeral=True)
            return conn.close()

        conn.close()

    @mod.subcommand()
    @interactions.slash_option(
        name=LocalizedName(english_us="number", french="nombre"),
        description=LocalizedDesc(english_us="Number of messages to delete. Default : 5", french="Nombre de messages à supprimer. Par défaut : 5"),
        opt_type=interactions.OptionType.INTEGER,
        required=False
    )
    async def clear(self, ctx: SlashContext, number: int = 5):
        guild = ctx.guild

        if os.path.exists(f"./Database/{guild.id}.db") is False:
            return await ctx.send(ErrorMessage.database_not_found(guild.id), ephemeral=True)

        print("test")

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        channel = ctx.channel
        deleted = await channel.purge(deletion_limit=number, return_messages=True)

        em = Embed(
            description=f"🧹・**{len(deleted)}** messages supprimés.",
            color=0xFF5A5A,
            timestamp=interactions.Timestamp.utcnow()
        )
        if ctx.author.discriminator == "0":
            em.set_author(name=f"{ctx.author.username}", icon_url=ctx.author.avatar.url)
        else:
            em.set_author(name=f"{ctx.author.username}#{ctx.author.discriminator}", icon_url=ctx.author.avatar.url)

        await ctx.send(embeds=em, ephemeral=True)

        logs_clear = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'clear'").fetchone()[0])

        conn.close()

        em2 = Embed(
            title="🧹・Nouveau clear",
            description=f"**{len(deleted)}** messages supprimés sur le serveur **{ctx.guild.name}** ({ctx.guild.id}).",
            color=0xFF5A5A,
            timestamp=interactions.Timestamp.utcnow()
        )
        em2.set_author(name=ctx.author.username, icon_url=ctx.member.user.avatar.url, url=ctx.member.user.avatar.url)
        em2.add_field(name="**Channel : **", value=f"ID : {channel.id} | Name : {channel.name} ({channel.mention})",
                      inline=False)
        em2.set_footer(text=f"Author ID : {ctx.author.id} | Name : {ctx.author.username}.")

        f_path = f"./src/utils/clear_log/temp_clear_log_{ctx.guild.id}.txt"

        with open(f_path, "w") as f:
            if ctx.author.discriminator == "0":
                f.write(f"Clear log from {ctx.channel.name} ({ctx.channel.id}) | Server : {ctx.guild.name} ({ctx.guild.id})\nAuthor : {ctx.author.username} ({ctx.author.id})\n\n")
            else:
                f.write(f"Clear log from {ctx.channel.name} ({ctx.channel.id}) | Server : {ctx.guild.name} ({ctx.guild.id})\nAuthor : {ctx.author.username}#{ctx.author.discriminator} ({ctx.author.id})\n\n")

            for message in deleted:
                if message.attachments:
                    for attachment in message.attachments:
                        f.write(f"{message.timestamp.now().strftime('%m/%d/%Y, %H:%M:%S')} | {message.author} : {message.content} + {attachment.url}\n")
                else:
                    f.write(f"{message.timestamp.now().strftime('%m/%d/%Y, %H:%M:%S')} | {message.author} : {message.content}\n")

        txt = io.FileIO(f_path, "r")

        file = interactions.File(file_name=f"clear-log.txt", file=txt)

        await logs_clear.send(embeds=em2, files=file)

        txt.close()

        os.remove(f_path)

    @mod.subcommand(
        sub_cmd_description=LocalizedDesc(
            english_us="To timeout a user for X seconds. If you think he/ she needs to rest.",
            french="Pour exclure temporairement un membre pendant X secondes."
        )
    )
    @interactions.slash_option(
        name=LocalizedName(english_us="user", french="membre"),
        description=LocalizedDesc(english_us="User to timeout.", french="Membre à timeout."),
        opt_type=interactions.OptionType.USER,
        required=True
    )
    @interactions.slash_option(
        name=LocalizedName(english_us="duration", french="durée"),
        description=LocalizedDesc(english_us="Duration (in seconds).", french="Durée (en secondes)."),
        opt_type=interactions.OptionType.INTEGER,
        required=True
    )
    @interactions.slash_option(
        name=LocalizedName(english_us="reason", french="raison"),
        description=LocalizedDesc(english_us="Reason of the timeout.", french="Raison de l'exclusion temporaire."),
        opt_type=interactions.OptionType.STRING,
        required=False
    )
    async def timeout(self, ctx: interactions.SlashContext, user: interactions.Member, duration: int,
                      reason: str = "Aucune raison"):
        tempo = interactions.Timestamp.utcnow() + timedelta(seconds=duration)

        guild = ctx.guild

        await user.edit(communication_disabled_until=tempo.isoformat(), reason=reason)
        await ctx.send(f"{user.mention} a été exclu pendant **{time_to_readable(guild.id, duration)}** pour **{reason}**.", ephemeral=True)

        # Partie Logs
        if os.path.exists(f"./Database/{guild.id}.db") is False:
            return

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        logs_timeout = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'timeout'").fetchone()[0])

        conn.close()

        em = Embed(
            title="🟠・Nouvelle exclusion temporaire",
            description=f"Un membre vient de se faire exclure temporairement de **{guild.name}**.",
            color=0xFF5A5A,
            timestamp=interactions.Timestamp.utcnow()
        )

        if ctx.author.discriminator == "0":
            em.add_field(name="__Staff :__", value=ctx.author.username, inline=True)
        else:
            em.add_field(name="__Staff :__", value=f"{ctx.author.username}#{ctx.author.discriminator}", inline=True)
        if user.discriminator == "0":
            em.add_field(name="__Membre :__", value=user.username, inline=True)
        else:
            em.add_field(name="__Membre :__", value=f"{user.username}#{user.discriminator}", inline=True)

        em.add_field(name="__Durée de l'exclusion :__", value=f"{time_to_readable(guild.id, duration)}", inline=True)
        em.add_field(name="__Raison :__", value=reason)
        em.set_footer(text=f"Staff ID : {ctx.author.id} | Member ID : {user.id}")

        await logs_timeout.send(embeds=em)

    @mod.subcommand(
        sub_cmd_description=LocalizedDesc(
            english_us="To untimeout a user.",
            french="Pour annuler l'exclusion temporaire d'un membre."
        )
    )
    @interactions.slash_option(
        name=LocalizedName(english_us="user", french="membre"),
        description=LocalizedDesc(english_us="User to untimeout.", french="Membre à untimeout."),
        opt_type=interactions.OptionType.USER,
        required=True
    )
    @interactions.slash_option(
        name=LocalizedName(english_us="reason", french="raison"),
        description=LocalizedDesc(english_us="Reason of the untimeout.", french="Raison de l'untimeout."),
        opt_type=interactions.OptionType.STRING,
        required=False
    )
    async def untimeout(self, ctx: interactions.SlashContext, user: interactions.Member, reason: str = "Aucune raison"):
        guild = ctx.guild

        await user.edit(communication_disabled_until=None, reason=reason)
        await ctx.send(f"L'exclusion de {user.mention} a été annulé pour **{reason}**.", ephemeral=True)

        if os.path.exists(f"./Database/{guild.id}.db") is False:
            return

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        logs_untimeout = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'timeout'").fetchone()[0])

        conn.close()

        # Partie Logs

        em = Embed(
            title="🟢・Fin d'exclusion temporaire",
            description=f"Un staff vient de retirer l'exclusion temporaire d'un membre sur **{guild.name}**.",
            color=0x4CFF4C,
            timestamp=interactions.Timestamp.utcnow()
        )

        if ctx.author.discriminator == "0":
            em.add_field(name="__Staff :__", value=ctx.author.username, inline=True)
        else:
            em.add_field(name="__Staff :__", value=f"{ctx.author.username}#{ctx.author.discriminator}", inline=True)
        if user.discriminator == "0":
            em.add_field(name="__Membre :__", value=user.username, inline=True)
        else:
            em.add_field(name="__Membre :__", value=f"{user.username}#{user.discriminator}", inline=True)

        em.add_field(name="__Raison :__", value=reason)
        em.set_footer(text=f"Staff ID : {ctx.author.id} | Member ID : {user.id}")

        await logs_untimeout.send(embeds=em)


def setup(bot):
    Mod(bot)