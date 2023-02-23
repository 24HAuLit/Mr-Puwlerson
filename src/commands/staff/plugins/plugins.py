import os
import sqlite3

import interactions


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
            return await ctx.send(":x: | **Seul le propriétaire du serveur peut utiliser cette commande.**", ephemeral=True)

        if os.path.exists(f"./Database/{ctx.guild.id}.db") is False:
            return

        conn = sqlite3.connect(f"./Database/{ctx.guild.id}.db")
        c = conn.cursor()

        c.execute(f"SELECT status FROM plugins WHERE name = '{plugin}'")
        if c.fetchone()[0] == status:
            return await ctx.send(f"Le plugin `{plugin}` est déjà `{status}` !")
        else:
            c.execute(f"UPDATE plugins SET status = '{status}' WHERE name = '{plugin}'")
            conn.commit()

            if status == 'true':
                await ctx.send(f"Le plugin `{plugin}` a bien été activé !")
            else:
                await ctx.send(f"Le plugin `{plugin}` a bien été désactivé !")

        conn.close()


def setup(bot):
    Plugins(bot)
