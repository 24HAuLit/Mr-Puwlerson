import interactions
from src.utils.checks import database_exists, is_admin
from src.utils.const import DATA
from src.listeners.suggestion.components.deny import modal_deny


class SuggestionDenied(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.component_callback("refuse")
    async def button_refuse(self, ctx: interactions.ComponentContext):
        if await database_exists(ctx) is not True:
            return

        if await is_admin(ctx) is not True:
            return

        await ctx.send_modal(modal_deny())

    @interactions.modal_callback("refuse_reason")
    async def modal_refuse(self, ctx, deny_short_response: str):
        result = self.bot.get_channel(DATA["main"]["suggest_result"])
        em = interactions.Embed(
            title="Suggestion refusé",
            url=ctx.message.jump_url,
            color=0xFF3C3C,
            timestamp=interactions.Timestamp.utcnow()
        )
        em.add_field(name="__**Suggestion : **__", value=ctx.message.embeds[0].description, inline=False)
        em.add_field(name="__**Raison : **__", value=f"{deny_short_response}", inline=False)
        if ctx.author.discriminator == "0":
            em.set_footer(icon_url=ctx.member.user.avatar_url, text=f"Suggestion refusé par {ctx.author.username}.")
        else:
            em.set_footer(icon_url=ctx.member.user.avatar_url,
                          text=f"Suggestion refusé par {ctx.author.username}#{ctx.author.discriminator}.")

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
