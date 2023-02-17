import sqlite3
import interactions
from datetime import datetime
from const import DATA
from src.listeners.suggestion.components.deny import modal_deny


class SuggestionDenied(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("refuse")
    async def button_refuse(self, ctx):
        guild = await ctx.get_guild()
        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        if c.execute("SELECT id FROM roles WHERE type = 'Admin'".format(ctx.author.id)).fetchone()[0] in ctx.author.roles \
                or c.execute("SELECT id FROM roles WHERE type = 'Owner'".format(ctx.author.id)).fetchone()[0] in ctx.author.roles:
            await ctx.popup(modal_deny())
        else:
            await ctx.send("Vous n'avez pas la permission de refuser une suggestion.", ephemeral=True)

        conn.close()

    @interactions.extension_modal("refuse_reason")
    async def modal_refuse(self, ctx, response: str):
        result = await interactions.get(self.bot, interactions.Channel, object_id=DATA["main"]["suggest_result"])
        em = interactions.Embed(
            title="Suggestion refusé",
            url=ctx.message.url,
            color=0xFF3C3C,
            timestamp=datetime.utcnow()
        )
        em.add_field(name="__**Suggestion : **__", value=ctx.message.embeds[0].description, inline=False)
        em.add_field(name="__**Raison : **__", value=f"{response}", inline=False)
        em.set_footer(icon_url=ctx.author.avatar_url,
                      text=f"Suggestion refusé par {ctx.author.name}#{ctx.author.discriminator}.")

        em1 = interactions.Embed(
            title=ctx.message.embeds[0].title,
            description=ctx.message.embeds[0].description,
            color=0xFF3C3C,
            timestamp=ctx.message.embeds[0].timestamp
        )
        em1.set_footer(icon_url=ctx.message.embeds[0].footer.icon_url, text=ctx.message.embeds[0].footer.text)

        await ctx.message.edit(embeds=em1, components=[])
        await ctx.send("Vous avez refusé cette suggestion.", ephemeral=True)
        await result.send(embeds=em)


def setup(bot):
    SuggestionDenied(bot)
