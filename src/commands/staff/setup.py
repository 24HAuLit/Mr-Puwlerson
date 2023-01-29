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
            pass
        else:
            await ctx.send("Vous n'avez pas la permissions d'executer cette commande.", ephemeral=True)
            return interactions.StopCommand()

    @setup.subcommand()
    async def server(self, ctx: interactions.CommandContext):
        """Permet de configurer les différents types de serveur."""
        await ctx.send("Quel type de serveur voulez-vous configurer ?", components=self.select_menu, ephemeral=True)

    @interactions.extension_component("select")
    async def select(self, ctx: interactions.ComponentContext, choice: list[str]):
        guild = await ctx.get_guild()
        channels = await ctx.guild.get_all_channels()

        if choice[0] == "main":
            conn = sqlite3.connect(f"./Database/{guild.id}.db")
            c = conn.cursor()

            c.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='ticket'""")
            if c.fetchone()[0] == 1:
                await ctx.send("'Ticket' database already created.", ephemeral=True)
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
                await ctx.send("'Blacklist' database already created.", ephemeral=True)
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
                await ctx.send("'Channels' database already created.", ephemeral=True)
            else:
                c.execute("""CREATE TABLE channels
                    (
                        name text,
                        id   integer
                    )""")
                for x in range(len(channels)):
                    if "'" in channels[x].name:
                        channel = channels[x].name.replace("'", "")
                        c.execute("""INSERT INTO channels VALUES ('{}', '{}')""".format(channel, channels[x].id))
                    else:
                        c.execute(
                            """INSERT INTO channels VALUES ('{}', '{}')""".format(channels[x].name, channels[x].id))
                if "'" in guild.name:
                    n_guild = guild.name.replace("'", "")
                    c.execute("""INSERT INTO channels VALUES ('{}', '{}')""".format(n_guild, guild.id))
                else:
                    c.execute("""INSERT INTO channels VALUES ('{}', '{}')""".format(guild, guild.id))
        else:
            await ctx.send("logs test", ephemeral=True)

        conn.commit()
        conn.close()

    @setup.subcommand()
    async def roles(self, ctx: interactions.CommandContext):
        guild = await ctx.get_guild()
        roles = await ctx.guild.get_all_roles()

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        c.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='roles'""")
        if c.fetchone()[0] == 1:
            for x in range(len(roles)):
                c.execute(f"""SELECT * from roles WHERE id = {roles[x].id}""")
                row = c.fetchone()
                if row is None:
                    if "'" in roles[x].name:
                        role = roles[x].name.replace("'", "")
                        c.execute("""INSERT INTO roles VALUES ('{}', '{}', NULL)""".format(role, roles[x].id))
                    else:
                        c.execute("""INSERT INTO roles VALUES ('{}', '{}', NULL)""".format(roles[x].name, roles[x].id))
            await ctx.send("**Roles** database already created.", ephemeral=True)
        else:
            c.execute("""CREATE TABLE roles
                            (
                                name text,
                                id   integer,
                                type text default NULL
                            )""")
            for x in range(len(roles)):
                if "'" in roles[x].name:
                    role = roles[x].name.replace("'", "")
                    c.execute("""INSERT INTO roles VALUES ('{}', '{}', NULL)""".format(role, roles[x].id))
                else:
                    c.execute(
                        """INSERT INTO roles VALUES ('{}', '{}', NULL)""".format(roles[x].name, roles[x].id))

        roles_menu = interactions.SelectMenu(
            custom_id="roles_menu",
            type=interactions.ComponentType.ROLE_SELECT,
            options=[
                interactions.SelectOption(
                    label=role,
                    value=role
                )
                for role in roles
            ]
        )

        await ctx.send("Quel role sera le role par default ?", components=roles_menu, ephemeral=True)
        conn.commit()
        conn.close()

    @interactions.extension_component("roles_menu")
    async def role_choice(self, ctx: interactions.ComponentContext, choice: list[str]):
        guild = await ctx.get_guild()
        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        c.execute("SELECT * from roles WHERE type = 'Default'")
        row = c.fetchone()

        if row[0] != choice[0].name:
            if row is not None:
                c.execute(f"UPDATE roles SET type = NULL WHERE name = '{row[0]}'")
                c.execute(f"SELECT type from roles WHERE name = '{choice[0].name}'")
                c.execute(f"UPDATE roles SET type = 'Default' WHERE name = '{choice[0].name}'")

                await ctx.send(f"**{row[0]}** n'est plus le role par défaut, il a été remplacé par **{choice[0].name}**.")
            else:
                c.execute(f"SELECT type from roles WHERE name = '{choice[0].name}'")
                c.execute(f"UPDATE roles SET type = 'Default' WHERE name = '{choice[0].name}'")
                await ctx.send(f"**{choice[0].name}** est désormais le role par défaut.")
        else:
            await ctx.send(f"**{choice[0].name}** est déjà le role par défaut.")

        conn.commit()
        conn.close()


def setup(bot):
    Setup(bot)
