import interactions
from datetime import datetime


class ModalAccept(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_modal("accept_reason")
    async def modal_accept(self, ctx, response: str):
        result = await interactions.get(self.bot, interactions.Channel, object_id=1011705768002727987)
        em = interactions.Embed(
            title="Suggestion accepté",
            url=ctx.message.url,
            color=0x00FF00,
            timestamp=datetime.utcnow()
        )
        em.add_field(name=f"__**Suggestion : **__", value=ctx.message.embeds[0].description, inline=False)
        em.add_field(name="__**Raison : **__", value=f"{response}", inline=False)
        em.set_footer(icon_url=ctx.member.user.avatar_url, text=f"Suggestion accepté par {ctx.author}.")

        em1 = interactions.Embed(
            title=ctx.message.embeds[0].title,
            description=ctx.message.embeds[0].description,
            color=0x00FF00,
            timestamp=ctx.message.embeds[0].timestamp
        )
        em1.set_footer(icon_url=ctx.message.embeds[0].footer.icon_url, text=ctx.message.embeds[0].footer.text)

        await ctx.message.edit(embeds=em1, components=[])
        await ctx.send("Vous avez accepté la suggestion", ephemeral=True)
        await result.send(embeds=em)


def setup(bot):
    ModalAccept(bot)
