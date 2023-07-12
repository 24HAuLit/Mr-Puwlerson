import interactions


class Survey(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    @interactions.option(description="Quelle sera la question ?", required=True)
    @interactions.option(description="Quels choix ?", required=True)
    @interactions.option(description="Durée du sondage", required=False)
    async def survey(self, ctx: interactions.CommandContext, question: str, choices: list[str], duration: int):
        em = interactions.Embed(
            title="Nouveau sondage",
            description=f"**{question}**",
            color=0x00FFC8
        )
        em.set_footer(text=f"Créé par {ctx.author.name}")
        em.add_field(name="Choix", value="\n".join(choices))
        if duration:
            em.add_field(name="Durée", value=f"{duration} secondes")
        await ctx.send(embeds=em)


def setup(bot):
    Survey(bot)
