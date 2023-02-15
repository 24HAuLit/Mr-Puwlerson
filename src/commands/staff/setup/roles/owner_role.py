import sqlite3
import interactions


class OwnerRole(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("owner_menu")
    async def owner_role_choice(self, ctx: interactions.ComponentContext, choice: list[str]):
        guild = await ctx.get_guild()
        roles = await ctx.guild.get_all_roles()

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        c.execute("SELECT * from roles WHERE type = 'Owner'")
        row = c.fetchone()

        if row is None:
            c.execute(f"SELECT type from roles WHERE id = '{choice[0].id}'")
            c.execute(f"UPDATE roles SET type = 'Owner' WHERE id = '{choice[0].id}'")
            await ctx.send(f"**{choice[0].name}** est désormais le role Owner.", ephemeral=True)
        elif row[1] == choice[0].id:
            await ctx.send(f"**{choice[0].name}** est déjà le role Owner.", ephemeral=True)
        else:
            c.execute(f"UPDATE roles SET type = NULL WHERE id = '{row[1]}'")
            c.execute(f"SELECT type from roles WHERE id = '{choice[0].id}'")
            c.execute(f"UPDATE roles SET type = 'Admin' WHERE id = '{choice[0].id}'")

            await ctx.send(f"**{row[0]}** n'est plus le role Owner, il a été remplacé par **{choice[0].name}**.",
                           ephemeral=True)

        admin_menu = interactions.SelectMenu(
            custom_id="admin_menu",
            type=interactions.ComponentType.ROLE_SELECT,
            options=[
                interactions.SelectOption(
                    label=role,
                    value=role
                )
                for role in roles
            ]
        )
        await ctx.send("Quel role sera le role Admin ?\n*C'est à dire le role qui sera la pour assister le role Owner*",
                       components=admin_menu, ephemeral=True)

        conn.commit()
        conn.close()


def setup(bot):
    OwnerRole(bot)
