import sqlite3
import interactions
from interactions import LocalizedName, LocalizedDesc
from src.utils.checks import database_exists, is_admin


class UnBlacklist(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.slash_command(
        description=LocalizedDesc(english_us="Unblacklist a member", french="Unblacklist un membre"),
        dm_permission=False
    )
    @interactions.slash_option(
        name=LocalizedName(english_us="user", french="membre"),
        description=LocalizedDesc(english_us="User to unblacklist", french="Membre à unblacklist"),
        opt_type=interactions.OptionType.USER,
        required=True
    )
    @interactions.slash_option(
        name=LocalizedName(english_us="reason", french="raison"),
        description=LocalizedDesc(english_us="Reason of the unblacklist", french="Raison du unblacklist"),
        opt_type=interactions.OptionType.STRING,
        required=False
    )
    async def unblacklist(self, ctx: interactions.SlashContext, user: interactions.User, reason: str = "Aucune raison"):
        if await database_exists(ctx) is not True:
            return

        if is_admin(ctx) is not True:
            return

        guild = ctx.guild

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        user_id = user.id
        reason = reason
        channel = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'blacklist'").fetchone()[0])

        c.execute("DELETE FROM blacklist WHERE user_id='{}'".format(user_id))
        conn.commit()
        conn.close()

        await ctx.send(f"{user.mention} ({user.id}) a bien été unblacklist.", ephemeral=True)

        if user.discriminator == "0":
            em = interactions.Embed(
                description=f"Le membre {user.username} a été unblacklist par {ctx.author.username}#{ctx.author.discriminator}",
                color=0x00FF00,
                timestamp=interactions.Timestamp.utcnow()
            )
        else:
            em = interactions.Embed(
                description=f"Le membre {user.username}#{user.discriminator} a été unblacklist par {ctx.author.username}#{ctx.author.discriminator}",
                color=0x00FF00,
                timestamp=interactions.Timestamp.utcnow()
            )
        em.set_footer(text=f"Staff ID : {ctx.author.id} | User ID : {user.id}")

        await channel.send(embeds=em)

        if ctx.author.discriminator == "0":
            em_dm = interactions.Embed(
                title="🔓・Unblacklist",
                description=f"Vous avez été unblacklist par **{ctx.author.username}** pour **{reason}**.\nVous "
                            f"avez été gentil, c'est bien, maintenant continuer sur cette voie.",
                color=0x00FF00,
                timestamp=interactions.Timestamp.utcnow()
            )
            em_dm.set_footer(icon_url=ctx.author.avatar_url, text=f"Staff : {ctx.author.username} ({ctx.author.id})")
        else:
            em_dm = interactions.Embed(
                title="🔓・Unblacklist",
                description=f"Vous avez été unblacklist par **{ctx.author.username}#{ctx.author.discriminator}** "
                            f"pour **{reason}**.\nVous avez été gentil, c'est bien, maintenant continuer sur "
                            f"cette voie.",
                color=0x00FF00,
                timestamp=interactions.Timestamp.utcnow()
            )
            em_dm.set_footer(icon_url=ctx.author.avatar_url,
                             text=f"Staff : {ctx.author.username}#{ctx.author.discriminator} ({ctx.author.id})")

        await user.send(embeds=em_dm)


def setup(bot):
    UnBlacklist(bot)
