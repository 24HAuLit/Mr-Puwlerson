import sqlite3
import interactions
from interactions import LocalizedName, LocalizedDesc

from src.utils.checks import database_exists, is_admin
from src.utils.message_config import ErrorMessage


class Blacklist(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.slash_command(dm_permission=False)
    @interactions.slash_option(
        name=LocalizedName(english_us="user", french="membre"),
        description=LocalizedDesc(english_us="User to blacklist", french="Membre à blacklist"),
        opt_type=interactions.OptionType.USER,
        required=True
    )
    @interactions.slash_option(
        name=LocalizedName(english_us="reason", french="raison"),
        description=LocalizedDesc(english_us="Reason of the blacklist", french="Raison du blacklist"),
        opt_type=interactions.OptionType.STRING,
        required=True
    )
    async def blacklist(self, ctx: interactions.SlashContext, user: interactions.User, reason: str):
        """Blacklist a user from the bot."""
        if await database_exists(ctx) is not True:
            return

        if await is_admin(ctx) is False:
            return await ctx.send(ErrorMessage.MissingPermissions(ctx.guild.id), ephemeral=True)

        guild = ctx.guild

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        channel = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'blacklist'").fetchone()[0])

        if c.execute("SELECT user_id FROM blacklist WHERE user_id = ?", (user.id,)).fetchone() is not None:
            conn.close()
            return await ctx.send(ErrorMessage.already_blacklisted(guild.id), ephemeral=True)

        c.execute("INSERT INTO blacklist VALUES (NULL, '{}', '{}')".format(user.id, reason))
        conn.commit()

        blacklist_id = c.execute("SELECT blacklist_id FROM blacklist WHERE user_id = ?", (user.id,)).fetchone()[0]
        conn.close()

        await ctx.send(f"{user.mention} ({user.id}) a bien été blacklist.", ephemeral=True)

        em = interactions.Embed(
            title="🔒・Blacklist",
            description=f"User **{user.username}** has been blacklisted by **{ctx.author.username}**.",
            color=0xFF0000,
            timestamp=interactions.Timestamp.utcnow()
        )
        em.add_field(name="Reason", value=reason)
        em.add_field(name="Blacklist ID", value=blacklist_id)
        em.set_footer(text=f"Staff ID : {ctx.author.id} | User ID : {user.id}")

        await channel.send(embeds=em)

        em_dm = interactions.Embed(
            title="🔒・Blacklist",
            description=f"You have got blacklisted by **{ctx.author.username}** for **{reason}**.\n"
                        "You will be unblacklisted if you are nice or after a certain time.",
            color=0xFF0000,
            timestamp=interactions.Timestamp.utcnow()
        )
        em_dm.set_footer(icon_url=ctx.author.avatar.url, text=f"Staff : {ctx.author.username} ({ctx.author.id}) | ID : {blacklist_id}")

        await user.send(embeds=em_dm)
