import asyncio
import sqlite3
import interactions
from datetime import datetime
from interactions.ext.enhanced import cooldown
from const import DATA
from src.listeners.suggestion.components.accept import suggest_accept
from src.listeners.suggestion.components.deny import suggest_deny


class Suggestion(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    counter = 0

    async def cooldown_err(self, ctx, amount):
        return await ctx.send(f"Tu dois encore attendre {amount} minutes avant de pouvoir réutiliser cette commande.",
                              ephemeral=True)

    @interactions.extension_command()
    @cooldown(minutes=10, error=cooldown_err, type="user")
    @interactions.option("Ecris ta suggestion ici.")
    async def suggest(self, ctx: interactions.CommandContext, suggestion: str):
        """Pour pouvoir proposer une suggestion."""
        guild = await ctx.get_guild()

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()
        c.execute(f'SELECT * from blacklist WHERE user_id = {int(ctx.author.id)}')
        row = c.fetchone()

        if row is not None:
            await ctx.send("Désolé, mais vous êtes blacklist. Vous ne pouvez donc pas envoyé de suggestion.", ephemeral=True)
        else:
            channel = await interactions.get(self.bot, interactions.Channel, object_id=DATA["main"]["suggestion"])
            self.counter += 1
            em = interactions.Embed(
                title="Nouvelle suggestion #%d" % self.counter,
                description=suggestion,
                color=0xFFF000,
                timestamp=datetime.utcnow()
            )
            em.set_footer(
                icon_url=ctx.member.user.avatar_url,
                text=f"Suggestion proposé par {ctx.author.username}#{ctx.author.discriminator}."
            )

            await ctx.send(f"Votre suggestion a bien été posté dans {channel.mention}", ephemeral=True)
            message = await channel.send(embeds=em, components=[suggest_accept(), suggest_deny()])
            await message.create_reaction("⬆️")
            await asyncio.sleep(1)
            await message.create_reaction("⬇️")

        conn.close()


def setup(bot):
    Suggestion(bot)
