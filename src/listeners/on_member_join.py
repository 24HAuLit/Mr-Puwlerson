import interactions
import sqlite3
import string
import random
from interactions.api.events import MemberAdd, Component
from src.utils.checks import database_exists


class OnUserJoin(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.listen(MemberAdd)
    async def on_guild_member_add(self, member: MemberAdd):
        if await database_exists(member) is not True:
            return

        conn = sqlite3.connect(f"./Database/{member.guild.id}.db")
        c = conn.cursor()

        # if c.execute("SELECT id FROM channels WHERE type = 'guild'").fetchone()[0] != member.guild.id:  # Je sais pas a quoi sa sert gamberge plus tard
        #     return conn.close()

        if c.execute("SELECT auto_role FROM config").fetchone()[0] == 1:
            id = c.execute("SELECT default_role FROM config").fetchone()[0]
            role = member.guild.get_role(id)
            await member.member.add_role(role)

        elif c.execute("SELECT auto_role FROM config").fetchone()[0] == 2:
            if member.bot is True:
                return conn.close()

            conn2 = sqlite3.connect(f"./Database/temp_join.db")
            c2 = conn2.cursor()

            c2.execute("INSERT INTO 'join' VALUES ('{}', '{}')".format(member.member.id, member.guild.id))
            conn2.commit()
            conn2.close()

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

            good_code = random.choice(lst)

            c.execute("INSERT INTO antiraid VALUES ('{}', '{}')".format(member.member.id, good_code))
            conn.commit()

            em = interactions.Embed(
                title="🚧・Verification",
                description=f"Salut à toi {member.member.mention}.\n\n"
                            f"Pour pouvoir accéder au serveur **{member.guild.name}**, il vous faudra appuyer sur le "
                            f"boutton contenant le code suivant :\n\n`{good_code}`",
                color=0xFFD500
            )

            await member.member.send(embeds=em, components=[button1, button2, button3])

            conn.close()

        else:
            return conn.close()

    @interactions.listen(Component)
    async def on_component(self, ctx: Component):
        if ctx.ctx.guild is not None:
            return

        conn2 = sqlite3.connect("./Database/temp_join.db")
        c2 = conn2.cursor()

        guild_id = c2.execute("SELECT guild_id FROM 'join' WHERE user_id = '{}'".format(ctx.ctx.user.id)).fetchone()[0]
        guild = await self.bot.fetch_guild(guild_id)

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        good_code = c.execute("SELECT code FROM antiraid WHERE member = '{}'".format(ctx.ctx.user.id)).fetchone()[0]

        if ctx.ctx.custom_id == good_code:
            c2.execute("DELETE FROM 'join' WHERE user_id = '{}'".format(ctx.ctx.user.id))
            conn2.commit()
            conn2.close()

            c.execute("DELETE FROM antiraid WHERE member = '{}'".format(ctx.ctx.user.id))
            conn.commit()

            await ctx.ctx.message.edit(components=[])
            await ctx.ctx.send("Vous avez appuyé sur le bon boutton. Vous êtes donc vérifié !")

            role = await guild.fetch_role(c.execute("SELECT default_role FROM config").fetchone()[0])

            member = await self.bot.fetch_member(ctx.ctx.user.id, guild.id)

            await member.add_role(role=role, reason="Verification passed")

            conn.close()
        else:
            await ctx.ctx.send("Vous n'avez pas appuyé sur le bon boutton !")
