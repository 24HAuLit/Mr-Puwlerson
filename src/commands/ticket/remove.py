import sqlite3

import interactions
from const import DATA


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
                    await ctx.send("Argument manquant : [User/Role]", ephemeral=True)
            else:
                await ctx.send("Vous ne pouvez pas utiliser cette commande dans ce salon.", ephemeral=True)
        else:
            await ctx.send(":x: Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            interactions.StopCommand()

        conn.close()


def setup(bot):
    RemoveMember(bot)
