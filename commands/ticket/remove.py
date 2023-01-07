import interactions
from const import DATA


class RemoveMember(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
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

        guild = await interactions.get(self.bot, interactions.Guild, object_id=DATA["main"]["guild"])
        channels = interactions.search_iterable(await guild.get_all_channels(),
                                                lambda c: c.parent_id == DATA["main"]["ticket"])

        if DATA["roles"]["Staff"] in ctx.author.roles or DATA["roles"]["Owner"] in ctx.author.roles:
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


def setup(bot):
    RemoveMember(bot)
