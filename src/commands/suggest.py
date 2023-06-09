import asyncio
import os
import sqlite3
import interactions
from datetime import datetime
from interactions.ext.enhanced import cooldown
from src.listeners.suggestion.components.accept import suggest_accept
from src.listeners.suggestion.components.deny import suggest_deny
from message_config import ErrorMessage


class Suggestion(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    counter = 0

    async def cooldown_err(self, ctx, amount):
        return await ctx.send(ErrorMessage.cooldown(ctx.guild_id, amount), ephemeral=True)

    @interactions.extension_command(dm_permission=False)
    @cooldown(minutes=10, error=cooldown_err, type="user")
    @interactions.option("Ecris ta suggestion ici.")
    async def suggest(self, ctx: interactions.CommandContext, suggestion: str):
        """Pour pouvoir proposer une suggestion."""
        guild = await ctx.get_guild()

        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return await ctx.send(ErrorMessage.database_not_found(guild.id), ephemeral=True)

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        c.execute(f"SELECT status FROM plugins WHERE name = 'suggestion'")
        if c.fetchone()[0] == 'false':
            return await ctx.send(ErrorMessage.PluginError(guild.id, 'suggestion'), ephemeral=True)

        c.execute(f'SELECT * from blacklist WHERE user_id = {int(ctx.author.id)}')
        row = c.fetchone()

        if row is not None:
            await ctx.send(ErrorMessage.BlacklistError(guild.id), ephemeral=True)
        else:
            channel = await interactions.get(self.bot, interactions.Channel, object_id=
            c.execute("SELECT id FROM channels WHERE type = 'suggest'").fetchone()[0])
            self.counter += 1
            em = interactions.Embed(
                title="Nouvelle suggestion #%d" % self.counter,
                description=suggestion,
                color=0xFFF000,
                timestamp=datetime.utcnow()
            )
            if ctx.author.discriminator == "0":
                em.set_footer(icon_url=ctx.member.user.avatar_url, text=f"Suggestion proposé par {ctx.author.username}.")
            else:
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
