import asyncio
import interactions
from datetime import datetime
from listeners.suggestion.components.accept import suggest_accept
from listeners.suggestion.components.deny import suggest_deny


class Suggestion(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    counter = 0

    @interactions.extension_command(
        name="suggest",
        description="Pour pouvoir proposer une suggestion.",
        dm_permission=False,
        options=[
            interactions.Option(
                name="suggestion",
                description="Ecris ta suggestion ici.",
                type=interactions.OptionType.STRING,
                required=True
            )
        ]
    )
    async def _suggest(self, ctx: interactions.CommandContext, suggestion: str):
        channel = await interactions.get(self.bot, interactions.Channel, object_id=1011704888679477369)
        self.counter += 1
        em = interactions.Embed(
            title="Nouvelle suggestion #%d" % self.counter,
            description=suggestion,
            color=0xFFF000,
            timestamp=datetime.utcnow()
        )
        em.set_footer(
            icon_url=ctx.member.user.avatar_url,
            text=f"Suggestion proposé par {ctx.author}."
        )

        await ctx.send(f"Votre suggestion a bien été posté dans {channel.mention}", ephemeral=True)
        message = await channel.send(embeds=em, components=[suggest_accept(), suggest_deny()])
        await message.create_reaction("⬆️")
        await asyncio.sleep(1)
        await message.create_reaction("⬇️")


def setup(bot):
    Suggestion(bot)
    