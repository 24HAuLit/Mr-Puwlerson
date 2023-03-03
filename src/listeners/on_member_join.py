import os
import interactions
import sqlite3
import string
import random


class OnUserJoin(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.good_code = None
        self.guild = None
        self.message = None

    @interactions.extension_listener(name="on_guild_member_add")
    async def on_guild_member_add(self, member: interactions.GuildMember):
        if os.path.exists("./Database/{}.db".format(member.guild_id)) is False:
            return

        conn = sqlite3.connect("./Database/{}.db".format(member.guild_id))
        c = conn.cursor()

        if c.execute("SELECT id FROM channels WHERE type = 'guild'").fetchone()[0] != member.guild_id:
            return conn.close()

        if c.execute("SELECT status FROM plugins WHERE name = 'auto-role'").fetchone()[0] == 'true':
            role = await interactions.get(self.bot, interactions.Role,
                                          object_id=c.execute("SELECT id FROM roles WHERE type = 'Default'").fetchone()[0])
            await member.add_role(role)

        elif c.execute("SELECT status FROM plugins WHERE name = 'verif'").fetchone()[0] == 'true':

            self.guild = await interactions.get(self.bot, interactions.Guild, object_id=member.guild_id)

            lst = []
            code1 = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
            code2 = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
            code3 = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))

            lst.append(code1)
            lst.append(code2)
            lst.append(code3)

            button1 = interactions.Button(style=interactions.ButtonStyle.SECONDARY, label=code1, custom_id=code1)
            button2 = interactions.Button(style=interactions.ButtonStyle.SECONDARY, label=code2, custom_id=code2)
            button3 = interactions.Button(style=interactions.ButtonStyle.SECONDARY, label=code3, custom_id=code3)

            self.good_code = random.choice(lst)

            em = interactions.Embed(
                title="🚧・Verification",
                description=f"Salut à toi {member.mention}.\n\n"
                            f"Pour pouvoir accéder au serveur **{member.guild.name}**, il vous faudra appuyer sur le "
                            f"boutton contenant le code suivant :\n\n`{self.good_code}`",
                color=0xFFD500
            )

            self.message = await member.send(embeds=em, components=[button1, button2, button3])

            conn.close()

        else:
            return conn.close()

    @interactions.extension_listener()
    async def on_component(self, component: interactions.ComponentContext):
        if component.guild_id is not None:
            return

        if component.custom_id == self.good_code:
            await self.message.delete()
            await component.send("Vous avez appuyé sur le bon boutton. Vous êtes donc vérifié !")

            conn = sqlite3.connect("./Database/{}.db".format(self.guild.id))
            c = conn.cursor()

            role = await interactions.get(self.bot, interactions.Role,
                                          object_id=c.execute("SELECT id FROM roles WHERE type = 'Default'").fetchone()[0])

            user = await interactions.get(self.bot, interactions.Member, object_id=component.user.id,
                                          parent_id=self.guild.id)

            await user.add_role(role=role, guild_id=self.guild.id, reason="Verification passed")

            conn.close()
        else:
            await component.send("Vous n'avez pas appuyé sur le bon boutton !")


def setup(bot):
    OnUserJoin(bot)
