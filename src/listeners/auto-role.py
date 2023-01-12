import interactions
from const import DATA


class AutoRole(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_listener(name="on_guild_member_add")
    async def on_guild_member_add(self, member: interactions.Member):
        role = await interactions.get(self.bot, interactions.Role, object_id=DATA["roles"]["Default"])
        await member.add_role(role)


def setup(bot):
    AutoRole(bot)
