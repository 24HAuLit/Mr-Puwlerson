import interactions
import os.path
import sqlite3
from interactions.api.events import RoleCreate, RoleUpdate, RoleDelete


class OnRole(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.listen(RoleCreate)
    async def on_role_create(self, role: RoleCreate):
        guild = role.guild

        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        c.execute("""INSERT INTO roles VALUES ('{}', '{}', '{}')""".format(role.role.name, role.role.id, None))

        conn.commit()
        conn.close()

        logs = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'create-role'").fetchone()[0])
        em = interactions.Embed(
            title="📝・Nouveau rôle",
            description=f"Un nouveau rôle vient d'être créé sur **{guild.name}** ({guild.id})",
            color=0x4CFF4C
        )
        em.add_field(name="**Nom : **", value=role.role.name, inline=True)
        em.add_field(name="**ID : **", value=role.role.id, inline=False)

        await logs.send(embeds=em)

    @interactions.listen(RoleUpdate)
    async def role_update(self, role: RoleUpdate):
        ...

    @interactions.listen(RoleDelete)
    async def role_delete(self, role: RoleDelete):
        ...
