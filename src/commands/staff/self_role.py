import sqlite3
import interactions
from os.path import exists
from discord import PartialEmoji
from message_config import ErrorMessage


class SelfRole(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.reaction = None
        self.role = None

    @interactions.extension_command()
    @interactions.option("Message's ID", required=True)
    @interactions.option("Emoji", required=True)
    @interactions.option("Role", required=True)
    async def self_role(self, ctx: interactions.CommandContext, message_id: str, emoji: str, role: interactions.Role):
        if exists(f"./Database/{ctx.guild.id}.db") is False:
            return await ctx.send(ErrorMessage.database_not_found(ctx.guild.id), ephemeral=True)

        conn = sqlite3.connect(f"./Database/{ctx.guild.id}.db")
        c = conn.cursor()

        admin_role, owner_role = c.execute("SELECT id FROM roles WHERE type = 'Admin'").fetchone()[0], \
            c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0]

        conn.close()

        if admin_role in ctx.author.roles:
            pass
        else:
            if owner_role in ctx.author.roles:
                pass
            else:
                if ctx.author.id == ctx.guild.owner_id:
                    pass
                else:
                    return await ctx.send(ErrorMessage.MissingPermissions(ctx.guild.id), ephemeral=True)

        test = [message.id async for message in ctx.channel.history(maximum=100)]

        if int(message_id) not in test:
            return await ctx.send(ErrorMessage.MessageNotFound(ctx.guild.id, message_id), ephemeral=True)

        message = await interactions.get(self.bot, interactions.Message, object_id=int(message_id),
                                         channel_id=ctx.channel.id)

        partial_emoji = PartialEmoji.from_str(emoji)
        emoji_id = partial_emoji.id

        emoji_snowflake = await interactions.Emoji.get(guild_id=ctx.guild.id, emoji_id=emoji_id, client=self.bot._http)

        self.reaction = emoji_snowflake
        self.role = role

        await message.create_reaction(self.reaction)
        await ctx.send(f"L'émoji {self.reaction.format} a bien été ajouté au message `{message.id}` !", ephemeral=True)

    @interactions.extension_listener()
    async def on_message_reaction_add(self, reaction: interactions.MessageReaction):
        if reaction.user_id == self.bot.me.id:
            return

        if reaction.emoji.id == self.reaction.id:

            message = await interactions.get(self.bot, interactions.Message, object_id=reaction.message_id)
            user = await interactions.get(self.bot, interactions.User, object_id=reaction.user_id)
            guild = await interactions.get(self.bot, interactions.Guild, object_id=reaction.guild_id)

            await message.remove_reaction_from(self.reaction, reaction.member)

            if self.role.id in reaction.member.roles:
                await reaction.member.remove_role(self.role)
                return await user.send(f"Le role **{self.role.name}** a bien été retiré sur le serveur **{guild.name}** !")
            else:
                await reaction.member.add_role(self.role)
                return await user.send(f"Le role **{self.role.name}** a bien été ajouté sur le serveur **{guild.name}** !")


def setup(bot):
    SelfRole(bot)
