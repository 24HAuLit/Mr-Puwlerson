import sqlite3

import interactions
from const import DATA


class AddMember(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
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
    async def add(self, ctx: interactions.CommandContext, user: interactions.User = None, role: interactions.Role = None):
        """Pour pouvoir ajouter quelqu'un ou un role au ticket."""

        guild = await ctx.get_guild()
        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles or \
                c.execute("SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0] in ctx.author.roles:

            channels = interactions.search_iterable(await guild.get_all_channels(),
                                                    lambda f: f.parent_id == DATA["main"]["ticket"])
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
                    await ctx.send("Argument manquant : [User/Role]", ephemeral=True)
            else:
                await ctx.send("Vous ne pouvez pas utiliser cette commande dans ce salon.", ephemeral=True)
        else:
            await ctx.send(":x: Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            interactions.StopCommand()

        conn.close()

def setup(bot):
    AddMember(bot)
