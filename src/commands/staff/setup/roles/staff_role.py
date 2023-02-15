import interactions
import sqlite3


class StaffRole(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("staff_menu")
    async def staff_role_choice(self, ctx: interactions.ComponentContext, choice: list[str]):
        guild = await ctx.get_guild()
        roles = await ctx.guild.get_all_roles()

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        c.execute("SELECT * from roles WHERE type = 'Staff'")
        row = c.fetchone()

        if row is None:
            c.execute(f"SELECT type from roles WHERE id = '{choice[0].id}'")
            c.execute(f"UPDATE roles SET type = 'Staff' WHERE id = '{choice[0].id}'")
            await ctx.send(f"**{choice[0].name}** est désormais le role Staff.", ephemeral=True)
        elif row[1] == choice[0].id:
            await ctx.send(f"**{choice[0].name}** est déjà le role Staff.", ephemeral=True)
        else:
            c.execute(f"UPDATE roles SET type = NULL WHERE id = '{row[1]}'")
            c.execute(f"SELECT type from roles WHERE id = '{choice[0].id}'")
            c.execute(f"UPDATE roles SET type = 'Staff' WHERE id = '{choice[0].id}'")

            await ctx.send(f"**{row[0]}** n'est plus le role par Staff, il a été remplacé par **{choice[0].name}**.",
                           ephemeral=True)

        owner_menu = interactions.SelectMenu(
            custom_id="owner_menu",
            type=interactions.ComponentType.ROLE_SELECT,
            options=[
                interactions.SelectOption(
                    label=role,
                    value=role
                )
                for role in roles
            ]
        )
        await ctx.send("Quel role sera le role Owner ?\n*C'est à dire le role du créateur du serveur*",
                       components=owner_menu, ephemeral=True)

        conn.commit()
        conn.close()


def setup(bot):
    StaffRole(bot)
