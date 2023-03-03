import os
import sqlite3
import interactions
from message_config import ErrorMessage


class Plugins(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    @interactions.option(
        type=interactions.OptionType.STRING,
        name="plugin",
        description="Plugin a activer/désactiver",
        required=True,
        choices=[
            interactions.Choice(name="Auto-role", value="auto-role"),
            interactions.Choice(name="Suggestion", value="suggestion"),
            interactions.Choice(name="Report", value="report"),
            interactions.Choice(name="Verification", value="verif"),
        ]
    )
    @interactions.option(
        type=interactions.OptionType.STRING,
        name="status",
        description="Status du plugin",
        required=True,
        choices=[
            interactions.Choice(name="Activer", value="true"),
            interactions.Choice(name="Désactiver", value="false")
        ]
    )
    async def plugins(self, ctx: interactions.CommandContext, plugin: str, status: str):
        """Permet d'activer/désactiver les plugins."""
        if ctx.author.id != ctx.guild.owner_id:
            return await ctx.send(ErrorMessage.OwnerOnly(), ephemeral=True)

        if os.path.exists(f"./Database/{ctx.guild.id}.db") is False:
            return await ctx.send(ErrorMessage.database_not_found(ctx.guild.id), ephemeral=True)

        conn = sqlite3.connect(f"./Database/{ctx.guild.id}.db")
        c = conn.cursor()

        c.execute(f"SELECT status FROM plugins WHERE name = '{plugin}'")
        if c.fetchone()[0] == status:
            return await ctx.send(f"Le plugin `{plugin}` est déjà `{status}` !", ephemeral=True)
        elif plugin == 'auto-role' and c.execute("SELECT status FROM plugins WHERE name = 'verif'").fetchone()[0] == 'true':
            return await ctx.send("Le plugin `Verification` est déjà activé, vous ne pouvez pas activer le plugin "
                                  "`Auto-role`. Si vous voulez activer le plugin `Auto-role`, désactivez le plugin "
                                  "`Verification`.", ephemeral=True)
        elif plugin == 'verif' and c.execute("SELECT status FROM plugins WHERE name = 'auto-role'").fetchone()[0] == 'true':
            return await ctx.send("Le plugin `Auto-role` est déjà activé, vous ne pouvez pas activer le plugin "
                                  "`Verification`. Si vous voulez activer le plugin `Verification`, désactivez le "
                                  "plugin `auto-role`.", ephemeral=True)
        else:
            c.execute(f"UPDATE plugins SET status = '{status}' WHERE name = '{plugin}'")
            conn.commit()

            if status == 'true':
                await ctx.send(f"Le plugin `{plugin}` a bien été activé !", ephemeral=True)
            else:
                await ctx.send(f"Le plugin `{plugin}` a bien été désactivé !", ephemeral=True)

        conn.close()


def setup(bot):
    Plugins(bot)
