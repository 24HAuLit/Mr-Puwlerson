import asyncio
import interactions
from interactions.ext.checks import dm_only
from datetime import datetime


class Question(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    qst_accept = interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="📩 Oui, envoyer",
        custom_id="send"
    )
    qst_deny = interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="Non, ne pas envoyer",
        custom_id="deny"
    )
    qst_rsp = interactions.Button(
        style=interactions.ButtonStyle.SECONDARY,
        label="Répondre",
        custom_id="response"
    )

    @interactions.extension_command(
        name="question",
        description="Pour pouvoir poser une question au staff.",
        options=[
            interactions.Option(
                name="question",
                description="Pose ta question. Tout abus sera sanctionné.",
                type=interactions.OptionType.STRING,
                required=True
            )
        ]
    )
    @dm_only()
    async def _question(self, ctx: interactions.CommandContext, question: str):
        await ctx.send("Êtes-vous sur de votre question ? **Tout abus se vera sanctionné !**",
                       components=[self.qst_accept, self.qst_deny])

        @interactions.extension_component("response")
        async def modal_response(_ctx):
            modal = interactions.Modal(
                title="Réponse",
                custom_id="question_response",
                components=[
                    interactions.TextInput(
                        style=interactions.TextStyleType.SHORT,
                        label="Que voulez-vous répondre ?",
                        custom_id="text_input_question_response",
                        min_length=1,
                        max_length=500
                    )
                ]
            )

            await _ctx.popup(modal)

        @interactions.extension_modal("question_response")
        async def modal_accept(_ctx, response: str):

            em2 = interactions.Embed(
                title="Un staff a répondu à votre question.",
                description=response,
                color=0x4FFF4F,
                timestamp=datetime.utcnow()
            )
            em2.set_footer(
                icon_url=_ctx.user.avatar_url,
                text=f"Staff : {_ctx.user}"
            )

            await ctx.send(embeds=em2)
            await _ctx.send(f"{_ctx.user.mention} a répondu a cette question.")

        @interactions.extension_component("deny")
        async def question_deny(_ctx):
            await ctx.edit(components=[])
            await _ctx.send("Vous avez annulé votre question.")

        @interactions.extension_component("send")
        async def question_accept(_ctx):
            return int(_ctx.user.id) == int(ctx.user.id)

        try:
            button_ctx: interactions.ComponentContext = await self.bot.wait_for_component(
                components=self.qst_accept, check=question_accept, timeout=15
            )
            channel = await interactions.get(self.bot, interactions.Channel, object_id=1019331289897238670)
            em = interactions.Embed(
                title="Nouvelle question",
                description=question,
                timestamp=datetime.utcnow()
            )
            em.set_footer(
                icon_url=ctx.user.avatar_url,
                text=f"Question envoyé par {ctx.user} | ID : {ctx.user.id}"
            )
            await ctx.edit(components=[])
            await button_ctx.send("Votre question a bien été envoyé !")
            await channel.send(embeds=em, components=self.qst_rsp)
        except asyncio.TimeoutError:
            return await ctx.edit(components=[])


def setup(bot):
    Question(bot)
