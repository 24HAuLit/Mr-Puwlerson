import interactions
from src.commands.ticket.tickets import Tickets
from interactions import LocalizedDesc
from src.utils.checks import is_staff, database_exists, ticket_parent
from src.utils.message_config import ErrorMessage


class AddMember(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @Tickets.ticket.subcommand(
        sub_cmd_description=LocalizedDesc(english_us="To add someone or a role to the ticket.", french="Pour pouvoir ajouter quelqu'un ou un role au ticket.")
    )
    @interactions.slash_option(
        name="option",
        description=LocalizedDesc(english_us="To add a user or a role to the ticket.", french="Pour ajouter un utilisateur ou un role au ticket."),
        opt_type=interactions.OptionType.MENTIONABLE,
        choices=[
            interactions.SlashCommandChoice(name="user", value="user"),
            interactions.SlashCommandChoice(name="role", value="role")
        ],
        required=True
    )
    async def add(self, ctx: interactions.SlashContext, option: interactions.Member | interactions.Role):

        if await database_exists(ctx) is not True:
            return

        if await is_staff(ctx) is not True:
            return

        if await ticket_parent(ctx) is not True:
            return

        guild = ctx.guild

        user = option if isinstance(option, interactions.Member) else None
        role = option if isinstance(option, interactions.Role) else None

        if user is not None:
            if guild.get_member(user.id) is None:
                return await ctx.send(ErrorMessage.UserNotFound(user.username, guild.id), ephemeral=True)

            for member in ctx.channel.members:
                if member.id == user.id:
                    return await ctx.send(ErrorMessage.UserAlreadyInTicket(user.username, guild.id), ephemeral=True)

            new_perms = [interactions.PermissionOverwrite(id=int(user.id), type=1,
                                                          allow=64 | 1024 | 2048 | 32768 | 65536 | 262144 | 2147483648)]
            await ctx.channel.edit(permission_overwrites=ctx.channel.permission_overwrites + new_perms)

            em = interactions.Embed(description=f"{user.mention} a été ajouter au ticket.", color=0x2ECC70)
            return await ctx.send(embeds=em)

        elif role is not None:
            if guild.get_role(role.id) is None:
                return await ctx.send(ErrorMessage.RoleNotFound(role, guild.id), ephemeral=True)

            print(ctx.channel.permissions_for(role))

            if ctx.channel.permissions_for(role).VIEW_CHANNEL is True:
                return await ctx.send("test", ephemeral=True)

            # for role in ctx.channel.roles:
            #     if role.id == role.id:
            #         return await ctx.send(ErrorMessage.RoleAlreadyInTicket(role.name, guild.id), ephemeral=True)

            new_perms = [interactions.PermissionOverwrite(id=int(role.id), type=0,
                                                          allow=64 | 1024 | 2048 | 32768 | 65536 | 262144 | 2147483648)]
            await ctx.channel.edit(permission_overwrites=ctx.channel.permission_overwrites + new_perms)
            em = interactions.Embed(description=f"{role.mention} a été ajouter au ticket.", color=0x2ECC70)
            return await ctx.send(embeds=em)


def setup(bot):
    AddMember(bot)
