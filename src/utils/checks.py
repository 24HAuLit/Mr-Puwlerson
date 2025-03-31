import interactions
from sqlite3 import connect
from os.path import exists
from src.utils.message_config import ErrorMessage


async def database_exists(ctx):
    """Check if the database exists
    :param ctx: interaction Context
    :return: Bool | Error message"""
    if (isinstance(ctx, interactions.events.discord.MessageReactionAdd)
            or isinstance(ctx, interactions.events.discord.MessageReactionRemove)
            or isinstance(ctx, interactions.events.discord.MessageReactionRemoveAll)
            or isinstance(ctx, interactions.events.discord.MessageReactionRemoveEmoji)
            or isinstance(ctx, interactions.events.discord.MessageCreate)
            or isinstance(ctx, interactions.events.discord.MessageUpdate)
            or isinstance(ctx, interactions.events.discord.MessageDelete)):
        ctx = ctx.message

    guild = ctx.guild

    if isinstance(ctx, interactions.models.internal.SlashContext):
        if not exists(f"./Database/{guild.id}.db"):
            return await ctx.message.reply(ErrorMessage.database_not_found(guild.id), ephemeral=True)
        else:
            return True
    elif isinstance(ctx, interactions.models.discord.components.InteractiveComponent):
        if not exists(f"./Database/{guild.id}.db"):
            return False
        else:
            return True
    else:
        if not exists(f"./Database/{guild.id}.db"):
            return await ctx.reply(ErrorMessage.database_not_found(guild.id), ephemeral=True)
        else:
            return True


async def is_staff(ctx):
    """Check if the user is staff
    :param ctx: interaction Context
    :return: True | Error message"""
    guild = ctx.guild
    conn = connect(f"./Database/{guild.id}.db")
    c = conn.cursor()

    owner_role = c.execute("SELECT owner_role FROM config").fetchone()[0]
    staff_role = c.execute("SELECT staff_role FROM config").fetchone()[0]

    if owner_role in ctx.author.roles or staff_role in ctx.author.roles or ctx.guild.is_owner(ctx.author):
        conn.close()
        return True
    else:
        conn.close()
        return await ctx.send(ErrorMessage.MissingPermissions(guild.id), ephemeral=True)


async def is_admin(ctx):
    """Check if the user is admin
    :param ctx: interaction Context
    :return: True | Error message"""
    guild = ctx.guild
    conn = connect(f"./Database/{guild.id}.db")
    c = conn.cursor()

    owner_role = c.execute("SELECT owner_role FROM config").fetchone()[0]
    admin_role = c.execute("SELECT admin_role FROM config").fetchone()[0]

    if owner_role in ctx.author.roles or admin_role in ctx.author.roles or ctx.guild.is_owner(ctx.author):
        conn.close()
        return True
    else:
        conn.close()
        return await ctx.send(ErrorMessage.MissingPermissions(guild.id), ephemeral=True)


async def is_owner(ctx):
    """Check if the user is owner of the guild
    :param ctx: interaction Context
    :return: True | Error message"""
    guild = ctx.guild
    conn = connect(f"./Database/{guild.id}.db")
    c = conn.cursor()

    if c.execute("SELECT owner_role FROM config").fetchone()[0] in ctx.author.roles or ctx.guild.is_owner(ctx.author):
        conn.close()
        return True
    else:
        conn.close()
        return await ctx.send(ErrorMessage.MissingPermissions(guild.id), ephemeral=True)


async def ticket_parent(ctx):
    """Check if the channel is a ticket parent
    :param ctx: interaction Context
    :return: True | Error message"""
    guild = ctx.guild
    conn = connect(f"./Database/{guild.id}.db")
    c = conn.cursor()

    if ctx.channel.parent_id == c.execute("SELECT ticket_parent FROM config").fetchone()[0]:
        conn.close()
        return True
    else:
        conn.close()
        return await ctx.send(ErrorMessage.ChannelError(guild.id), ephemeral=True)


async def is_plugin(ctx, plugin: str):
    """Check if the plugin is enabled or not
    :param ctx: interaction Context
    :param plugin: plugin name
    :return: True | Error message"""
    guild = ctx.guild
    conn = connect(f"./Database/{guild.id}.db")
    c = conn.cursor()

    if c.execute(f"SELECT status FROM plugins WHERE name = '{plugin}'").fetchone()[0] == 'true':
        conn.close()
        return True
    else:
        conn.close()
        return await ctx.send(ErrorMessage.PluginError(guild.id, plugin), ephemeral=True)


async def is_blacklist(ctx, author_id: int):
    """Check if the user is blacklisted
    :param ctx: interaction Context
    :param author_id: user id
    :return: bool | Error message"""
    guild = ctx.guild
    conn = connect(f"./Database/{guild.id}.db")
    c = conn.cursor()

    if c.execute(f"SELECT * FROM blacklist WHERE user_id = {author_id}").fetchone() is not None:
        conn.close()
        await ctx.send(ErrorMessage.BlacklistError(guild.id), ephemeral=True)
        return True
    else:
        conn.close()
        return False


async def is_cooldown(ctx):
    """Check if there is a cooldown
    :param ctx: interaction Context
    :return: bool | Error message"""
    guild = ctx.guild

    conn = connect(f"./Database/{guild.id}.db")
    c = conn.cursor()
    timestamp = c.execute(f"SELECT timestamp FROM cooldown WHERE user = {ctx.author.id}").fetchone()[0]

    if timestamp >= int(interactions.Timestamp.utcnow().timestamp()):
        conn.close()
        timestamp = timestamp - int(interactions.Timestamp.utcnow().timestamp())

        await ctx.send(ErrorMessage.cooldown(guild.id, timestamp), ephemeral=True)
        return True
    else:
        conn.close()
        return False
