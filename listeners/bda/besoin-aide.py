import interactions


class BesoinAide(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_listener(name="on_voice_state_update")
    async def bda_join(self, ctx: interactions.CommandContext):
        print("test")


def setup(bot):
    BesoinAide(bot)
