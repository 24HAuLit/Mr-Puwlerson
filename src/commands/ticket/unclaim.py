import os
import sqlite3
import interactions
from message_config import ErrorMessage


class UnClaimCommand(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(dm_permission=False)
    async def unclaim(self, ctx: interactions.CommandContext):
        """Pour pouvoir retirer sa revendication d'un ticket."""
        guild = await ctx.get_guild()

        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return await ctx.send(ErrorMessage.database_not_found(guild.id), ephemeral=True)

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        channels = interactions.search_iterable(await guild.get_all_channels(),
                                                lambda f: f.parent_id == c.execute(
                                                    "SELECT id FROM channels WHERE type = 'ticket_parent'").fetchone()[
                                                    0])
        channel = await ctx.get_channel()

        if c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles or \
                c.execute("SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0] in ctx.author.roles:

            # Partie Database
            c.execute(f'SELECT * from ticket WHERE channel_id = {int(channel.id)}')
            row = c.fetchone()

            if channel in channels:
                if int(ctx.author.id) == row[2]:
                    c.execute(f"UPDATE ticket SET staff_id = 'None' WHERE channel_id = {int(channel.id)}")
                    conn.commit()
                    em = interactions.Embed(
                        description=f"Le ticket n'est plus pris en charge par {ctx.author.mention}.",
                        color=0xFF4646
                    )
                    await ctx.send(embeds=em)
                else:
                    await ctx.send("Vous ne pouvez pas faire cela car vous n'avez pas revendiqué le ticket.",
                                   ephemeral=True)
            else:
                await ctx.send(ErrorMessage.ChannelError(guild.id), ephemeral=True)
        else:
            await ctx.send(ErrorMessage.MissingPermissions(guild.id), ephemeral=True)
            interactions.StopCommand()

        conn.close()


def setup(bot):
    UnClaimCommand(bot)
