import sqlite3
import interactions
from interactions import LocalizedName, LocalizedDesc
from src.utils.checks import database_exists, is_admin
from src.utils.message_config import ErrorMessage


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

        if await is_admin(ctx) is False:
            return await ctx.send(ErrorMessage.MissingPermissions(ctx.guild.id), ephemeral=True)

        guild = ctx.guild

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        user_id = user.id
        reason = reason
        channel = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'blacklist'").fetchone()[0])

        if c.execute(f"SELECT user_id FROM blacklist WHERE user_id = {user_id}").fetchone() is None:
            conn.close()
            return await ctx.send("Sorry, but you can't unblacklist someone who is not blacklist.", ephemeral=True)

        blacklist_id = c.execute(f"SELECT blacklist_id FROM blacklist WHERE user_id = {user_id}").fetchone()[0]

        c.execute("DELETE FROM blacklist WHERE user_id='{}'".format(user_id))
        conn.commit()
        conn.close()

        await ctx.send(f"{user.mention} ({user.id}) is no longer blacklisted.", ephemeral=True)

        em = interactions.Embed(
            title="🔓・Unblacklist",
            description=f"User **{user.username}** has been unblacklisted by **{ctx.author.username}**",
            color=0x00FF00,
            timestamp=interactions.Timestamp.utcnow()
        )
        em.add_field(name="Reason", value=reason)
        em.add_field(name="Blacklist ID", value=blacklist_id)
        em.set_footer(text=f"Staff ID : {ctx.author.id} | User ID : {user.id}")

        await channel.send(embeds=em)

        em_dm = interactions.Embed(
            title="🔓・Unblacklist",
            description=f"Vous have been unblacklisted by **{ctx.author.username}** for **{reason}**.\nYou "
                        f"had been nice, it's good, now continue on this path.",
            color=0x00FF00,
            timestamp=interactions.Timestamp.utcnow()
        )
        em_dm.set_footer(icon_url=ctx.author.avatar_url, text=f"Staff : {ctx.author.username} ({ctx.author.id}) | "
                                                              f"ID : {blacklist_id}")

        await user.send(embeds=em_dm)


def setup(bot):
    UnBlacklist(bot)
