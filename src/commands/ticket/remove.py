import os
import sqlite3
import interactions
from message_config import ErrorMessage


class RemoveMember(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(dm_permission=False)
    @interactions.option(
        description="Pour retirer un membre au ticket",
        required=False
    )
    @interactions.option(
        description="Pour retirer un role au ticket",
        required=False
    )
    async def remove(self, ctx: interactions.CommandContext, user: interactions.User = None,
                     role: interactions.Role = None):
        """Pour pouvoir retirer quelqu'un ou un role au ticket."""
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
                if user is not None:
                    perms = [interactions.Overwrite(id=int(user.id), type=1,
                                                    deny=2199023255551)]
                    await ctx.channel.modify(permission_overwrites=ctx.channel.permission_overwrites + perms)
                    em = interactions.Embed(description=f"{user.mention} a été retiré du ticket.", color=0xFF5A5A)
                    await ctx.send(embeds=em)
                elif role is not None:
                    perms = [interactions.Overwrite(id=int(role.id), type=0,
                                                    deny=2199023255551)]
                    await ctx.channel.modify(permission_overwrites=ctx.channel.permission_overwrites + perms)
                    em = interactions.Embed(description=f"{role.mention} a été retiré du ticket.", color=0xFF5A5A)
                    await ctx.send(embeds=em)
                else:
                    await ctx.send(ErrorMessage.MissingRequiredArgument(guild.id, "User/ Role"), ephemeral=True)
            else:
                await ctx.send(ErrorMessage.ChannelError(guild.id), ephemeral=True)
        else:
            await ctx.send(ErrorMessage.MissingPermissions(guild.id), ephemeral=True)
            interactions.StopCommand()

        conn.close()


def setup(bot):
    RemoveMember(bot)
