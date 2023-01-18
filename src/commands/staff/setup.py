import interactions
import sqlite3
from interactions.ext.checks import is_owner


class Setup(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.select_menu = interactions.SelectMenu(
            custom_id="select",
            options=[
                interactions.SelectOption(label="Serveur principal", value="main"),
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

        else:
            await ctx.send("logs test", ephemeral=True)

        conn.commit()
        conn.close()


def setup(bot):
    Setup(bot)
