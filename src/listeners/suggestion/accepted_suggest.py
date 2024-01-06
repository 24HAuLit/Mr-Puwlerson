import interactions
from src.utils.checks import database_exists, is_admin
from src.utils.const import DATA
from src.listeners.suggestion.components.accept import modal_accept


class SuggestionAccepted(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.component_callback("accept")
    async def button_accept(self, ctx: interactions.ComponentContext):
        if await database_exists(ctx) is not True:
            return

        if await is_admin(ctx) is not True:
            return

        await ctx.send_modal(modal_accept())

    @interactions.modal_callback("accept_reason")
    async def modal_accept(self, ctx: interactions.ModalContext, acc_short_response: str):
        result = self.bot.get_channel(DATA["main"]["suggest_result"])
        em = interactions.Embed(
            title="Suggestion accepté",
            url=ctx.message.jump_url,
            color=0x00FF00,
            timestamp=interactions.Timestamp.utcnow()
        )
        em.add_field(name=f"__**Suggestion : **__", value=ctx.message.embeds[0].description, inline=False)
        em.add_field(name="__**Raison : **__", value=f"{acc_short_response}", inline=False)

        if ctx.author.discriminator == "0":
            em.set_footer(icon_url=ctx.member.avatar.url, text=f"Suggestion accepté par {ctx.author.username}.")
        else:
            em.set_footer(icon_url=ctx.member.avatar.url,
                          text=f"Suggestion accepté par {ctx.author.username}#{ctx.author.discriminator}.")

        em1 = interactions.Embed(
            title=ctx.message.embeds[0].title,
            description=ctx.message.embeds[0].description,
            color=0x00FF00,
            timestamp=ctx.message.embeds[0].timestamp
        )
        em1.set_footer(icon_url=ctx.message.embeds[0].footer.icon_url, text=ctx.message.embeds[0].footer.text)

        await ctx.message.edit(embeds=em1, components=[])
        await ctx.send("Vous avez accepté la suggestion.", ephemeral=True)
        await result.send(embeds=em)

