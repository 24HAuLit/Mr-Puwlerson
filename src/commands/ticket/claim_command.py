import os
import sqlite3
import interactions
from message_config import ErrorMessage


class ClaimCommand(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(dm_permission=False)
    async def claim(self, ctx: interactions.CommandContext):
        """Pour pouvoir revendiquer un ticket."""
        guild = await ctx.get_guild()

        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return await ctx.send(ErrorMessage.database_not_found(guild.id), ephemeral=True)

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles or \
                c.execute("SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0] in ctx.author.roles:
            channels = interactions.search_iterable(await guild.get_all_channels(),
                                                    lambda f: f.parent_id == c.execute("SELECT id FROM channels WHERE "
                                                                                       "type = "
                                                                                       "'ticket_parent'").fetchone()[0])
            channel = await ctx.get_channel()
            id_staff = ctx.author.id

            # Partie Database
            c.execute(f'SELECT * from ticket WHERE channel_id = {int(channel.id)}')
            row = c.fetchone()

            # Partie commande
            if channel in channels:
                if row[2] is None or row[2] == 'None':
                    c.execute(f"UPDATE ticket SET staff_id = {id_staff} WHERE channel_id = {int(channel.id)}")

                    conn.commit()
                    em = interactions.Embed(
                        description=f"Le ticket a été pris en charge par {ctx.author.mention}.",
                        color=0x2ECC70
                    )
                    await ctx.send(embeds=em)
                else:
                    await ctx.send(f"<@{row[2]}> a déjà pris en charge ce ticket.", ephemeral=True)
            else:
                await ctx.send(ErrorMessage.ChannelError(guild.id), ephemeral=True)
        else:
            await ctx.send(ErrorMessage.MissingPermissions(guild.id), ephemeral=True)
            interactions.StopCommand()

        conn.close()


def setup(bot):
    ClaimCommand(bot)
