import os
import sqlite3
import interactions
from message_config import ErrorMessage


class Rename(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(dm_permission=False)
    @interactions.option("Nouveau nom pour le ticket")
    async def rename(self, ctx: interactions.CommandContext, nom: str):
        """Pour pouvoir renommer un ticket."""
        guild = await ctx.get_guild()

        if os.path.exists(f"./Database/{guild.id}.db") is False:
            return await ctx.send(ErrorMessage.database_not_found(guild.id), ephemeral=True)

        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        channels = interactions.search_iterable(await guild.get_all_channels(),
                                                lambda f: f.parent_id == c.execute("SELECT id FROM channels WHERE "
                                                                                   "type = "
                                                                                   "'ticket_parent'").fetchone()[0])

        if c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles or \
                c.execute("SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0] in ctx.author.roles:
            if ctx.channel in channels:
                await ctx.channel.modify(name=nom)
                await ctx.send(f"Le ticket vient d'être renommé **{nom}**.", ephemeral=True)
            else:
                await ctx.send(ErrorMessage.ChannelError(), ephemeral=True)
        else:
            await ctx.send(ErrorMessage.MissingPermissions(), ephemeral=True)
            interactions.StopCommand()

        conn.close()


def setup(bot):
    Rename(bot)
