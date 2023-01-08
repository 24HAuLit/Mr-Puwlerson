import interactions


class Presence(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_listener()
    async def on_start(self):
        await self.bot.change_presence(
            interactions.ClientPresence(
                status=interactions.StatusType.DND,
                activities=[
                    interactions.PresenceActivity(
                        name="l'avenir de ce monde",
                        type=interactions.PresenceActivityType.COMPETING
                    )
                ]
            )
        )


def setup(bot):
    Presence(bot)
