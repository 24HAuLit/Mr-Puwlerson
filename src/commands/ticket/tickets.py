from interactions import Extension, Client, slash_command, SlashContext


class Tickets(Extension):
    def __init__(self, bot):
        self.bot: Client = bot

    @slash_command()
    async def ticket(self, ctx: SlashContext):
        pass
