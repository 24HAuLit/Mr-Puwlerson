import os
import sqlite3
import interactions


class Update(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    async def update(self, ctx: interactions.CommandContext):
        """Mise à jour de la base de données du serveur si nécessaire."""
        if ctx.author.id == ctx.guild.owner_id:
            pass
        else:
            return await ctx.send("❌・Vous n'avez pas l'autorisation d'utiliser cette commande.")

        if os.path.exists("./Database/{}.db".format(ctx.guild_id)) is False:
            return await ctx.send("❌・La base de données n'a pas encore été configurée. Pour la configurer, `/setup "
                                  "server`.")

        await ctx.send("Commande en cours de développement...", ephemeral=True)
        # await ctx.send("🔄・Mise à jour de la base de données en cours...")


def setup(bot):
    Update(bot)
