import interactions
from interactions.ext.checks import has_role


class RemoveMember(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(
        name="remove",
        description="Pour pouvoir retirer quelqu'un ou un role au ticket."
    )
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
    @has_role(1018602650566139984, 419532166888816640)
    async def _add(self, ctx: interactions.CommandContext, user: interactions.Member = None,
                   role: interactions.Role = None):
        guild = await interactions.get(self.bot, interactions.Guild, object_id=419529681885331456)
        channels = interactions.search_iterable(await guild.get_all_channels(),
                                                lambda c: c.parent_id == 1027647411495129109)
        if ctx.channel in channels:
            if user is not None:
                perms = [interactions.Overwrite(id=int(user.id), type=1,
                                                deny=2199023255551)]
                await ctx.channel.modify(permission_overwrites=ctx.channel.permission_overwrites + perms)
                em = interactions.Embed(description=f"{user.mention} a été retirer du ticket.", color=0xFF5A5A)
                await ctx.send(embeds=em)
            elif role is not None:
                perms = [interactions.Overwrite(id=int(role.id), type=0,
                                                deny=2199023255551)]
                await ctx.channel.modify(permission_overwrites=ctx.channel.permission_overwrites + perms)
                em = interactions.Embed(description=f"{role.mention} a été retirer du ticket.", color=0xFF5A5A)
                await ctx.send(embeds=em)
            else:
                await ctx.send("Argument manquant : [User/Role]", ephemeral=True)
        else:
            await ctx.send("Vous ne pouvez pas utiliser cette commande dans ce salon.", ephemeral=True)


def setup(bot):
    RemoveMember(bot)
