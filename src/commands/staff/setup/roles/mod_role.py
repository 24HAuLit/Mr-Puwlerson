import interactions
import sqlite3


class ModRole(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("mod_menu")
    async def mod_role_choice(self, ctx: interactions.ComponentContext, choice: list[str]):
        guild = await ctx.get_guild()
        roles = await ctx.guild.get_all_roles()

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        c.execute("SELECT * from roles WHERE type = 'Mod'")
        row = c.fetchone()

        if row is None:
            c.execute(f"SELECT type from roles WHERE id = '{choice[0].id}'")
            c.execute(f"UPDATE roles SET type = 'Mod' WHERE id = '{choice[0].id}'")
            await ctx.send(f"**{choice[0].name}** est désormais le role Modérateur.", ephemeral=True)
        elif row[1] == choice[0].id:
            await ctx.send(f"**{choice[0].name}** est déjà le role Modérateur.", ephemeral=True)
        else:
            c.execute(f"UPDATE roles SET type = NULL WHERE id = '{row[1]}'")
            c.execute(f"SELECT type from roles WHERE id = '{choice[0].id}'")
            c.execute(f"UPDATE roles SET type = 'Mod' WHERE id = '{choice[0].id}'")

            await ctx.send(f"**{row[0]}** n'est plus le role Modérateur, il a été remplacé par **{choice[0].name}**.",
                           ephemeral=True)

        await ctx.send("La configuration des roles est terminée, vous pouvez donc passer à la suite des "
                       "configurations ou utiliser le bot", ephemeral=True)
        conn.commit()
        conn.close()


def setup(bot):
    ModRole(bot)
