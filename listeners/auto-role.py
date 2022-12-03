import interactions


class AutoRole(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_listener(name="on_guild_member_add")
    async def on_guild_member_add(self, member: interactions.Member):
        role = await interactions.get(self.bot, interactions.Role, object_id=419556483861053448)
        await member.add_role(role)


def setup(bot):
    AutoRole(bot)
