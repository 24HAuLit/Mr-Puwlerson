import sqlite3
import interactions
from interactions import LocalizedDesc
from src.utils.checks import is_owner, database_exists


class Plugins(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.slash_command(
        description=LocalizedDesc(english_us="Activate or deactivate plugins", french="Active ou désactive des plugins"),
        dm_permission=False
    )
    @interactions.slash_option(
        opt_type=interactions.OptionType.STRING,
        name="plugin",
        description="Plugin a activer/désactiver",
        required=True,
        choices=[
            interactions.SlashCommandChoice(name="Suggestion", value="suggestion"),
            interactions.SlashCommandChoice(name="Report", value="report"),
            interactions.SlashCommandChoice(name="Giveaway", value="giveaway"),
        ]
    )
    @interactions.slash_option(
        opt_type=interactions.OptionType.STRING,
        name="status",
        description="Status du plugin",
        required=True,
        choices=[
            interactions.SlashCommandChoice(name="Activer", value="true"),
            interactions.SlashCommandChoice(name="Désactiver", value="false")
        ]
    )
    async def plugins(self, ctx: interactions.SlashContext, plugin: str, status: str):
        if await database_exists(ctx) is not True:
            return

        if await is_owner(ctx) is not True:
            return

        conn = sqlite3.connect(f"./Database/{ctx.guild.id}.db")
        c = conn.cursor()

        c.execute(f"SELECT status FROM plugins WHERE name = '{plugin}'")
        if c.fetchone()[0] == status:
            conn.close()
            return await ctx.send(f"Le plugin `{plugin}` est déjà `{status}` !", ephemeral=True)

        elif plugin == 'giveaway':
            if status == 'true':
                choice_modal = interactions.Modal(
                    interactions.ShortText(
                        label="Veuillez entrer l'ID du salon",
                        custom_id="giveaway_channel_text",
                        min_length=1,
                        max_length=100
                    ),
                    title="Choix du salon",
                    custom_id="giveaway_channel"
                )
                await ctx.send_modal(choice_modal)
            else:
                c.execute(f"UPDATE plugins SET status = '{status}' WHERE name = '{plugin}'")
                conn.commit()
                await ctx.send(f"Le plugin `{plugin}` a bien été désactivé !", ephemeral=True)

        else:
            print("else")
            c.execute(f"UPDATE plugins SET status = '{status}' WHERE name = '{plugin}'")
            conn.commit()

            if status == 'true':
                await ctx.send(f"Le plugin `{plugin}` a bien été activé !", ephemeral=True)
            else:
                await ctx.send(f"Le plugin `{plugin}` a bien été désactivé !", ephemeral=True)

        conn.close()

    @interactions.modal_callback("giveaway_channel")
    async def giveaway_channel(self, ctx: interactions.ComponentContext, giveaway_channel_text: int):
        # if type(giveaway_channel_text) is not int:
        #     return await ctx.send("Veuillez entrer un ID valable !", ephemeral=True)

        conn = sqlite3.connect(f"./Database/{ctx.guild.id}.db")
        c = conn.cursor()

        channel = self.bot.get_channel(giveaway_channel_text)

        c.execute(f"UPDATE plugins SET status = 'true' WHERE name = 'giveaway'")

        db_channel = c.execute(f"SELECT * FROM channels WHERE type = 'giveaway'").fetchone()

        if db_channel is None:
            print("if")
            if c.execute(f"SELECT id FROM channels WHERE id = {channel.id}").fetchone() is None:
                c.execute(
                    """INSERT INTO channels VALUES ('{}', '{}', '{}', '{}')""".format(channel.name, channel.id,
                                                                                      "giveaway", 0))
            else:
                c.execute(f"UPDATE channels SET type = 'giveaway' WHERE id = {channel.id}")

            conn.commit()
            conn.close()

            return await ctx.send(f"Le plugin `giveaway` a bien été activé !", ephemeral=True)

        elif db_channel[1] == channel.id:
            print("elif")
            conn.commit()
            conn.close()
            return await ctx.send(f"Le salon `{channel.name}` est déjà le salon des giveaways !", ephemeral=True)

        else:
            print("else")
            c.execute(f"UPDATE channels SET type = NULL WHERE id = {db_channel[1]}")
            c.execute(f"UPDATE channels SET type = 'giveaway' WHERE id = {channel.id}")

            conn.commit()
            conn.close()
            return await ctx.send(f"Le salon des giveaways a bien été changé pour `{channel.name}` !", ephemeral=True)


def setup(bot):
    Plugins(bot)
