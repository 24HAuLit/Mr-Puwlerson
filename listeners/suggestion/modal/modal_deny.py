import interactions
from datetime import datetime


class ModalDeny(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_modal("refuse_reason")
    async def modal_refuse(self, ctx, response: str):
        result = await interactions.get(self.bot, interactions.Channel, object_id=1011705768002727987)
        em = interactions.Embed(
            title="Suggestion refusé",
            url=ctx.message.url,
            color=0xFF3C3C,
            timestamp=datetime.utcnow()
        )
        em.add_field(name="__**Suggestion : **__", value=ctx.message.embeds[0].description, inline=False)
        em.add_field(name="__**Raison : **__", value=f"{response}", inline=False)
        em.set_footer(icon_url=ctx.member.user.avatar_url, text=f"Suggestion refusé par {ctx.author}.")

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
    ModalDeny(bot)
