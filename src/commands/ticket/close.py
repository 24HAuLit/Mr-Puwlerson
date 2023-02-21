import sqlite3
import interactions
from src.listeners.ticket.components.close import confirm_close


class CloseTicketCommand(interactions.Extension):

    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(dm_permission=False)
    async def close(self, ctx: interactions.CommandContext):
        """Pour pouvoir fermer le ticket."""
        guild = await ctx.get_guild()
        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles or \
                c.execute("SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0] in ctx.author.roles:
            channels = interactions.search_iterable(await guild.get_all_channels(),
                                                    lambda f: f.parent_id == c.execute("SELECT id FROM channels WHERE "
                                                                                       "type = "
                                                                                       "'ticket_parent'").fetchone()[0])
            if ctx.channel in channels:
                await ctx.send("Êtes-vous sur de vouloir fermer ce ticket ?", components=confirm_close(),
                               ephemeral=True)
            else:
                await ctx.send("Vous ne pouvez pas utiliser cette commande dans ce salon.", ephemeral=True)
        else:
            await ctx.send(":x: Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            interactions.StopCommand()

        conn.close()


def setup(bot):
    CloseTicketCommand(bot)
