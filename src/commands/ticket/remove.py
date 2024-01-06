import interactions
from interactions import LocalizedDesc
from src.utils.checks import is_staff, database_exists, ticket_parent


class RemoveMember(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.slash_command(dm_permission=False)
    @interactions.slash_option(
        name="option",
        description=LocalizedDesc(english_us="To remove a user or a role to the ticket.",
                                  french="Pour retirer un utilisateur ou un role au ticket."),
        opt_type=interactions.OptionType.MENTIONABLE,
        choices=[
            interactions.SlashCommandChoice(name="user", value="user"),
            interactions.SlashCommandChoice(name="role", value="role")
        ],
        required=True
    )
    async def remove(self, ctx: interactions.SlashContext, option: interactions.Member | interactions.Role):
        if await database_exists(ctx) is not True:
            return

        if await is_staff(ctx) is not True:
            return

        if await ticket_parent(ctx) is not True:
            return

        user = option if isinstance(option, interactions.Member) else None
        role = option if isinstance(option, interactions.Role) else None

        if user is not None:
            perms = [interactions.PermissionOverwrite(id=int(user.id), type=1, deny=2199023255551)]
            await ctx.channel.edit(permission_overwrites=ctx.channel.permission_overwrites + perms)

            em = interactions.Embed(description=f"{user.mention} a été retiré du ticket.", color=0xFF5A5A)
            await ctx.send(embeds=em)

        elif role is not None:
            perms = [interactions.PermissionOverwrite(id=int(role.id), type=0, deny=2199023255551)]
            await ctx.channel.edit(permission_overwrites=ctx.channel.permission_overwrites + perms)

            em = interactions.Embed(description=f"{role.mention} a été retiré du ticket.", color=0xFF5A5A)
            await ctx.send(embeds=em)


def setup(bot):
    RemoveMember(bot)
