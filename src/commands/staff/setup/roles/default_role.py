import interactions
import sqlite3


class DefaultRole(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("default_menu")
    async def default_role_choice(self, ctx: interactions.ComponentContext, choice: list[str]):
        guild = await ctx.get_guild()
        roles = await ctx.guild.get_all_roles()

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        c.execute("SELECT * from roles WHERE type = 'Default'")
        row = c.fetchone()

        if row is None:
            c.execute(f"SELECT type from roles WHERE id = '{choice[0].id}'")
            c.execute(f"UPDATE roles SET type = 'Default' WHERE id = '{choice[0].id}'")
            await ctx.send(f"**{choice[0].name}** est désormais le role par défaut.", ephemeral=True)
        elif row[1] == choice[0].id:
            await ctx.send(f"**{choice[0].name}** est déjà le role par défaut.", ephemeral=True)
        else:
            c.execute(f"UPDATE roles SET type = NULL WHERE id = '{row[1]}'")
            c.execute(f"SELECT type from roles WHERE id = '{choice[0].id}'")
            c.execute(f"UPDATE roles SET type = 'Default' WHERE id = '{choice[0].id}'")

            await ctx.send(f"**{row[0]}** n'est plus le role par défaut, il a été remplacé par **{choice[0].name}**.",
                           ephemeral=True)

        staff_menu = interactions.SelectMenu(
            custom_id="staff_menu",
            type=interactions.ComponentType.ROLE_SELECT,
            options=[
                interactions.SelectOption(
                    label=role,
                    value=role
                )
                for role in roles
            ]
        )
        await ctx.send("Quel role sera le role Staff ?\n*C'est a dire le role qui aura accès aux tickets, commande "
                       "staff...*", components=staff_menu, ephemeral=True)

        conn.commit()
        conn.close()


def setup(bot):
    DefaultRole(bot)
