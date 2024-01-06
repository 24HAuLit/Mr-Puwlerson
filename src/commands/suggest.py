import asyncio
import sqlite3
import interactions
from interactions import LocalizedDesc
from src.listeners.suggestion.components.accept import suggest_accept
from src.listeners.suggestion.components.deny import suggest_deny
from src.utils.checks import database_exists, is_plugin, is_blacklist, is_cooldown


class Suggestion(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.counter = 0

    @interactions.slash_command(
        description=LocalizedDesc(english_us="To be able to propose a suggestion.",
                                  french="Pour pouvoir proposer une suggestion."),
        dm_permission=False
    )
    @interactions.slash_option(
        name="suggestion",
        description=LocalizedDesc(english_us="Your suggestion.", french="Votre suggestion."),
        opt_type=3,
        required=True
    )
    async def suggest(self, ctx: interactions.SlashContext, suggestion: str):
        if await database_exists(ctx) is not True:
            return

        guild = ctx.guild

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if await is_plugin(ctx, "suggestion") is not True:
            return

        if await is_blacklist(ctx, ctx.author.id) is True:
            return

        if c.execute("SELECT * FROM cooldown").fetchone() is None:
            c.execute("INSERT INTO cooldown VALUES ('{}', '{}')".format(ctx.author.id, 0))
            conn.commit()

        if await is_cooldown(ctx, "suggestion"):
            return

        timestamp = int(interactions.Timestamp.utcnow().timestamp()) + c.execute("SELECT suggestion_cooldown FROM config").fetchone()[0]

        c.execute(f"UPDATE cooldown SET suggestion = {timestamp} WHERE user = {ctx.author.id}")
        conn.commit()

        channel = self.bot.get_channel(c.execute("SELECT id FROM channels WHERE type = 'suggest'").fetchone()[0])
        self.counter += 1
        em = interactions.Embed(
            title="Nouvelle suggestion #%d" % self.counter,
            description=suggestion,
            color=0xFFF000,
            timestamp=interactions.Timestamp.utcnow()
        )
        if ctx.author.discriminator == "0":
            em.set_footer(icon_url=ctx.member.avatar.url, text=f"Suggestion proposé par {ctx.author.username}.")
        else:
            em.set_footer(
                icon_url=ctx.member.avatar.url,
                text=f"Suggestion proposé par {ctx.author.username}#{ctx.author.discriminator}."
            )

        await ctx.send(f"Votre suggestion a bien été posté dans {channel.mention}", ephemeral=True)
        message = await channel.send(embeds=em, components=[suggest_accept(), suggest_deny()])
        await message.add_reaction("⬆️")
        await asyncio.sleep(1)
        await message.add_reaction("⬇️")

        conn.close()
