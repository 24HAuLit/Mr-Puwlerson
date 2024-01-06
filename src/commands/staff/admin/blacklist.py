import os
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
        if await database_exists(ctx) is not True:
            return

        if await is_admin(ctx) is not True:
            return

        guild = ctx.guild

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        channel = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'blacklist'").fetchone()[0])

        if c.execute("SELECT user_id FROM blacklist WHERE user_id = ?", (user.id,)).fetchone() is not None:
            conn.close()
            return await ctx.send(ErrorMessage.already_blacklisted(guild.id), ephemeral=True)

        c.execute("INSERT INTO blacklist VALUES (NULL, '{}', '{}')".format(user.id, reason))
        conn.commit()
        conn.close()

        await ctx.send(f"{user.mention} ({user.id}) a bien été blacklist.", ephemeral=True)

        if ctx.author.discriminator == "0":
            if user.discriminator == "0":
                em = interactions.Embed(
                    title="🔒・Blacklist",
                    description=f"Le membre **{user.username}** a été blacklist par **{ctx.author.username}**.",
                    color=0xFF0000,
                    timestamp=interactions.Timestamp.utcnow()
                )
            else:
                em = interactions.Embed(
                    title="🔒・Blacklist",
                    description=f"Le membre **{user.username}#{user.discriminator}** a été blacklist par **{ctx.author.username}**.",
                    color=0xFF0000,
                    timestamp=interactions.Timestamp.utcnow()
                )
        else:
            if user.discriminator == "0":
                em = interactions.Embed(
                    title="🔒・Blacklist",
                    description=f"Le membre **{user.username}** a été blacklist par **{ctx.author.username}#{ctx.author.discriminator}**",
                    color=0xFF0000,
                    timestamp=interactions.Timestamp.utcnow()
                )
            else:
                em = interactions.Embed(
                    title="🔒・Blacklist",
                    description=f"Le membre **{user.username}#{user.discriminator}** a été blacklist par **{ctx.author.username}#{ctx.author.discriminator}**",
                    color=0xFF0000,
                    timestamp=interactions.Timestamp.utcnow()
                )
        em.add_field(name="Raison", value=reason)
        em.set_footer(text=f"Staff ID : {ctx.author.id} | User ID : {user.id}")

        await channel.send(embeds=em)

        if ctx.author.discriminator == "0":
            em_dm = interactions.Embed(
                title="🔒・Blacklist",
                description=f"Vous avez été blacklist par **{ctx.author.username}** pour **{reason}**.\nVous pourrez être unblacklist si vous êtes gentil ou après un certain temps.",
                color=0xFF0000,
                timestamp=interactions.Timestamp.utcnow()
            )
            em_dm.set_footer(icon_url=ctx.author.avatar.url,
                             text=f"Staff : {ctx.author.username} ({ctx.author.id})")
        else:
            em_dm = interactions.Embed(
                title="🔒・Blacklist",
                description=f"Vous avez été blacklist par **{ctx.author.username}#{ctx.author.discriminator}** pour **{reason}**.\nVous pourrez être unblacklist si vous êtes gentil ou après un certain temps.",
                color=0xFF0000,
                timestamp=interactions.Timestamp.utcnow()
            )
            em_dm.set_footer(icon_url=ctx.author.avatar.url,
                             text=f"Staff : {ctx.author.username}#{ctx.author.discriminator} ({ctx.author.id})")

        await user.send(embeds=em_dm)
