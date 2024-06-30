import interactions
import sqlite3

from src.utils.checks import database_exists


class Report(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.slash_command(dm_permission=False)
    @interactions.slash_option(
        name=interactions.LocalizedName(english_us="channel", french="salon"),
        description=interactions.LocalizedDesc(english_us="Channel to look at", french="Salon ou regarder"),
        opt_type=interactions.OptionType.CHANNEL,
        required=True
    )
    @interactions.slash_option(
        name=interactions.LocalizedName(english_us="problem", french="probleme"),
        description=interactions.LocalizedDesc(english_us="What's happening", french="Quel est le problème"),
        opt_type=interactions.OptionType.STRING,
        required=True
    )
    @interactions.slash_option(
        name=interactions.LocalizedName(english_us="user", french="utilisateur"),
        description=interactions.LocalizedDesc(english_us="Optional: a specific user to report", french="Optionnel: un utilisateur spécifique à signaler"),
        opt_type=interactions.OptionType.USER,
        required=False
    )
    async def report(self, ctx: interactions.SlashContext, channel: interactions.GuildChannel, problem: str, user: interactions.User = None):
        """Report a problem with a channel."""
        if await database_exists(ctx) is not True:
            return

        guild = ctx.guild

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        log_channel = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'report'").fetchone()[0])

        if user is not None:
            c.execute("INSERT INTO reports VALUES ('{}', '{}', '{}', '{}')".format(ctx.author.id, user.id, channel.id, problem))
        else:
            c.execute("INSERT INTO reports VALUES ('{}', NULL, '{}', '{}')".format(ctx.author.id, channel.id, problem))

        conn.commit()
        conn.close()

        await ctx.send(f"Reported the problem to the staff.", ephemeral=True)

        if ctx.author.discriminator == "0":
            if user is not None:
                em = interactions.Embed(
                    title="🔒・Report",
                    description=f"**{ctx.author.username}** reported a problem with **{user.username}** in **{channel.name}**.",
                    color=0xFF0000,
                    timestamp=interactions.Timestamp.utcnow()
                )
            else:
                em = interactions.Embed(
                    title="🔒・Report",
                    description=f"**{ctx.author.username}** reported a problem in **{channel.name}**.",
                    color=0xFF0000,
                    timestamp=interactions.Timestamp.utcnow()
                )
        else:
            if user is not None:
                em = interactions.Embed(
                    title="🔒・Report",
                    description=f"**{ctx.author.username}#{ctx.author.discriminator}** reported a problem with **{user.username}#{user.discriminator}** in **{channel.name}**.",
                    color=0xFF0000,
                    timestamp=interactions.Timestamp.utcnow()
                )
            else:
                em = interactions.Embed(
                    title="🔒・Report",
                    description=f"**{ctx.author.username}#{ctx.author.discriminator}** reported a problem in **{channel.name}**.",
                    color=0xFF0000,
                    timestamp=interactions.Timestamp.utcnow()
                )

        em.add_field(name="Problem", value=problem)

        await log_channel.send(embed=em)
