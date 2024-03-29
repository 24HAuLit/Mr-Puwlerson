import os
import sqlite3
import interactions
from message_config import ErrorMessage


class AddMember(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(dm_permission=False)
    @interactions.option(
        type=interactions.OptionType.USER,
        name="user",
        description="Pour ajouter un membre au ticket",
        required=False
    )
    @interactions.option(
        type=interactions.OptionType.ROLE,
        name="role",
        description="Pour ajouter un role au ticket",
        required=False
    )
    async def add(self, ctx: interactions.CommandContext, user: interactions.User = None,
                  role: interactions.Role = None):
        """Pour pouvoir ajouter quelqu'un ou un role au ticket."""
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
            if ctx.channel in channels:
                if user is not None:
                    new_perms = [interactions.Overwrite(id=int(user.id), type=1,
                                                        allow=64 | 1024 | 2048 | 32768 | 65536 | 262144 | 2147483648)]
                    await ctx.channel.modify(permission_overwrites=ctx.channel.permission_overwrites + new_perms)
                    em = interactions.Embed(description=f"{user.mention} a été ajouter au ticket.", color=0x2ECC70)
                    await ctx.send(embeds=em)
                elif role is not None:
                    new_perms = [interactions.Overwrite(id=int(role.id), type=0,
                                                        allow=64 | 1024 | 2048 | 32768 | 65536 | 262144 | 2147483648)]
                    await ctx.channel.modify(permission_overwrites=ctx.channel.permission_overwrites + new_perms)
                    em = interactions.Embed(description=f"{role.mention} a été ajouter au ticket.", color=0x2ECC70)
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
    AddMember(bot)
