import interactions
import sqlite3


class Setup(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.select_menu = interactions.SelectMenu(
            custom_id="select",
            options=[
                interactions.SelectOption(label="Serveur principal", description="Faites le une fois que vous avez "
                                                                                 "crée tout les channels dont vous "
                                                                                 "avez besoins", value="main"),
                interactions.SelectOption(label="Serveur de logs", value="logs")
            ]
        )

    @interactions.extension_command()
    async def setup(self, ctx: interactions.CommandContext):
        if ctx.author.id == ctx.guild.owner_id:
            await ctx.send("Quel type de serveur voulez-vous configurer ?", components=self.select_menu, ephemeral=True)
        else:
            await ctx.send("Vous n'avez pas la permissions d'executer cette commande.", ephemeral=True)

    @interactions.extension_component("select")
    async def select(self, ctx: interactions.ComponentContext, choice: list[str]):
        guild = await ctx.get_guild()

        if choice[0] == "main":
            conn = sqlite3.connect(f"./Database/{guild.id}.db")
            c = conn.cursor()

            c.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='ticket'""")
            if c.fetchone()[0] == 1:
                pass
            else:
                c.execute("""CREATE TABLE "ticket"
                    (
                        ticket_id  INTEGER not null
                            primary key autoincrement,
                        author_id  INTEGER not null,
                        staff_id   INTEGER not null,
                        channel_id INTEGER
                    )""")

            c.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='blacklist'""")
            if c.fetchone()[0] == 1:
                pass
            else:
                c.execute("""CREATE TABLE blacklist
                    (
                        blacklist_id integer not null
                            primary key autoincrement,
                        user_id      integer not null,
                        reason       text
                    )""")

            c.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='channels'""")
            if c.fetchone()[0] == 1:
                pass
            else:
                c.execute("""CREATE TABLE channels
                    (
                        name text,
                        id   integer
                    )""")
                channels = await ctx.guild.get_all_channels()
                for x in range(len(channels)):
                    if "'" in channels[x].name:
                        channel = channels[x].name.replace("'", "")
                        c.execute("""INSERT INTO channels VALUES ('{}', '{}')""".format(channel, channels[x].id))
                    else:
                        c.execute("""INSERT INTO channels VALUES ('{}', '{}')""".format(channels[x].name, channels[x].id))
                if "'" in guild.name:
                    n_guild = guild.name.replace("'", "")
                    c.execute("""INSERT INTO channels VALUES ('{}', '{}')""".format(n_guild, guild.id))
                else:
                    c.execute("""INSERT INTO channels VALUES ('{}', '{}')""".format(guild, guild.id))

            c.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='roles'""")
            if c.fetchone()[0] == 1:
                pass
            else:
                c.execute("""CREATE TABLE roles
                    (
                        name text,
                        id   integer
                    )""")
                roles = await ctx.guild.get_all_roles()
                for x in range(len(roles)):
                    if "'" in roles[x].name:
                        role = roles[x].name.replace("'", "")
                        c.execute("""INSERT INTO roles VALUES ('{}', '{}')""".format(role, roles[x].id))
                    else:
                        c.execute("""INSERT INTO roles VALUES ('{}', '{}')""".format(roles[x].name, roles[x].id))
        else:
            await ctx.send("logs test", ephemeral=True)

        conn.commit()
        conn.close()


def setup(bot):
    Setup(bot)
