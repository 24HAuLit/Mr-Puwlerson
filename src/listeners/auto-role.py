import os
import interactions
import sqlite3


class AutoRole(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_listener(name="on_guild_member_add")
    async def on_guild_member_add(self, member: interactions.GuildMember):
        if os.path.exists("./Database/{}.db".format(member.guild_id)) is False:
            return

        conn = sqlite3.connect("./Database/{}.db".format(member.guild_id))
        c = conn.cursor()

        c.execute("SELECT status FROM plugins WHERE name = 'auto-role'")
        if c.fetchone()[0] == 'false':
            return

        role = await interactions.get(self.bot, interactions.Role, object_id=c.execute("SELECT id FROM roles WHERE type = 'Default'").fetchone()[0])
        await member.add_role(role)
        conn.close()


def setup(bot):
    AutoRole(bot)
