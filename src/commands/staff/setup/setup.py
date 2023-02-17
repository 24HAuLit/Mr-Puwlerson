import interactions
import sqlite3


class Setup(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.select_menu = interactions.SelectMenu(
            custom_id="server_type",
            options=[
                interactions.SelectOption(label="Serveur principal", description="Faites le une fois que vous avez "
                                                                                 "crée tout les channels dont vous "
                                                                                 "avez besoins", value="main"),
                interactions.SelectOption(label="Serveur de logs", description="A faire une fois le serveur principal "
                                                                               "configuré.", value="logs")
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

    @interactions.extension_component("server_type")
    async def select(self, ctx: interactions.ComponentContext, choice: list[str]):
        guild = await ctx.get_guild()
        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        if choice[0] == "main":
            c.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='blacklist'""")
            if c.fetchone()[0] == 1:
                await ctx.send("**Blacklist** database already created.", ephemeral=True)
            else:
                c.execute("""CREATE TABLE blacklist
                    (
                        blacklist_id integer not null
                            primary key autoincrement,
                        user_id      integer not null,
                        reason       text
                    )""")
                await ctx.send("**Blacklist** database created.", ephemeral=True)
            await ctx.send("Configuration du serveur principal terminée. Vous pouvez désormais configurer les "
                           "channels et les roles", ephemeral=True)
        else:
            await ctx.send("Logs test : Work in progress", ephemeral=True)

        conn.commit()
        conn.close()

    @setup.subcommand()
    async def channels(self, ctx: interactions.CommandContext):
        """Permet de configurer les différents channels du serveur principal."""
        guild = await ctx.get_guild()
        channels = await ctx.guild.get_all_channels()

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        c.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='channels'""")
        if c.fetchone()[0] == 1:
            for x in range(len(channels)):
                c.execute(f"""SELECT * from channels WHERE id = {channels[x].id}""")
                row = c.fetchone()
                if row is None:
                    if "'" in channels[x].name:
                        channel = channels[x].name.replace("'", "")
                        c.execute(
                            """INSERT INTO channels VALUES ('{}', '{}', NULL, '{}')""".format(channel, channels[x].id,
                                                                                              0))
                    else:
                        c.execute(
                            """INSERT INTO channels VALUES ('{}', '{}', NULL, '{}')""".format(channels[x].name,
                                                                                              channels[x].id, 0))
                else:
                    if "'" in channels[x].name:
                        channel = channels[x].name.replace("'", "")
                        c.execute(f"""UPDATE channels SET name = '{channel}' WHERE id = {channels[x].id}""")
                    else:
                        c.execute(f"""UPDATE channels SET name = '{channels[x].name}' WHERE id = {channels[x].id}""")

            c.execute(f"""SELECT * from channels WHERE id = {guild.id}""")
            row = c.fetchone()
            if row is None:
                if "'" in guild.name:
                    n_guild = guild.name.replace("'", "")
                    c.execute(
                        """INSERT INTO channels VALUES ('{}', '{}', 'guild', '{}')""".format(n_guild, guild.id, 0))
                else:
                    c.execute(
                        """INSERT INTO channels VALUES ('{}', '{}', 'guild', '{}')""".format(guild.name, guild.id, 0))
            else:
                if "'" in guild.name:
                    n_guild = guild.name.replace("'", "")
                    c.execute(f"""UPDATE channels SET name = '{n_guild}' WHERE id = {guild.id}""")
                    c.execute(f"""UPDATE channels SET type = 'guild' WHERE id = {guild.id}""")
                else:
                    c.execute(f"""UPDATE channels SET name = '{guild.name}' WHERE id = {guild.id}""")
                    c.execute(f"""UPDATE channels SET type = 'guild' WHERE id = {guild.id}""")
        else:
            c.execute("""CREATE TABLE channels
                (
                    name text,
                    id   integer,
                    type text default NULL,
                    hidden integer default 0
                )""")
            for x in range(len(channels)):
                if "'" in channels[x].name:
                    channel = channels[x].name.replace("'", "")
                    c.execute(
                        """INSERT INTO channels VALUES ('{}', '{}', NULL, '{}')""".format(channel, channels[x].id, 0))
                else:
                    c.execute(
                        """INSERT INTO channels VALUES ('{}', '{}', NULL, '{}')""".format(channels[x].name,
                                                                                          channels[x].id, 0))

            if "'" in guild.name:
                n_guild = guild.name.replace("'", "")
                c.execute(
                    """INSERT INTO channels VALUES ('{}', '{}', '{}', '{}')""".format(n_guild, guild.id, "guild", 0))
            else:
                c.execute(
                    """INSERT INTO channels VALUES ('{}', '{}', '{}', '{}')""".format(guild.name, guild.id, "guild", 0))

        banned_channels = interactions.SelectMenu(
            custom_id="banned_channels",
            placeholder="Sélectionnez les channels qui seront cachés dans les logs.",
            max_values=len(channels),
            min_values=1,
            options=[
                interactions.SelectOption(label=channels[x].name, value=str(channels[x].id), default=False)
                for x in range(len(channels))
            ]
        )

        await ctx.send("Sélectionnez les channels qui seront cachés dans les logs.", components=banned_channels,
                       ephemeral=True)

        conn.commit()
        conn.close()

    @setup.subcommand()
    async def roles(self, ctx: interactions.CommandContext):
        """Permet de configurer les différents roles du serveur principal."""
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

        default_menu = interactions.SelectMenu(
            custom_id="default_menu",
            type=interactions.ComponentType.ROLE_SELECT,
            options=[
                interactions.SelectOption(
                    label=role,
                    value=role
                )
                for role in roles
            ]
        )

        await ctx.send("Quel role sera le role par default ?", components=default_menu, ephemeral=True)
        conn.commit()
        conn.close()

    @setup.subcommand()
    async def tickets(self, ctx: interactions.CommandContext):
        """Permet de configurer les différents salons nécessaires au bon fonctionnement des tickets."""
        guild = await ctx.get_guild()
        channels = await ctx.guild.get_all_channels()

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        c.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='ticket'""")
        if c.fetchone()[0] == 1:
            await ctx.send("La table tickets existe déjà.", ephemeral=True)
        else:
            c.execute("""CREATE TABLE "ticket"
                                (
                                    ticket_id  INTEGER not null
                                        primary key autoincrement,
                                    author_id  INTEGER not null,
                                    staff_id   INTEGER not null,
                                    channel_id INTEGER
                                )""")
            c.execute("""CREATE TABLE "ticket_count"
                                (
                                    user_id INTEGER PRIMARY KEY,
                                    count INTEGER DEFAULT 0
                                )""")
            await ctx.send("La table tickets a été créée.", ephemeral=True)

        ticket_category = interactions.SelectMenu(
            custom_id="ticket_category",
            placeholder="Sélectionnez la catégorie des tickets.",
            max_values=1,
            min_values=1,
            options=[
                interactions.SelectOption(label=channels[x].name, value=str(channels[x].id), default=False)
                for x in range(len(channels))
            ]
        )

        await ctx.send("Sélectionnez la catégorie des tickets.", components=ticket_category, ephemeral=True)

        conn.commit()
        conn.close()


def setup(bot):
    Setup(bot)
