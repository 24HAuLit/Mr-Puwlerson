import sqlite3
import interactions
from interactions import LocalizedDesc
from interactions.api.events import MessageReactionAdd
from src.utils.checks import database_exists, is_admin
from src.utils.message_config import ErrorMessage
from discord import PartialEmoji


class SelfRole(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.slash_command(
        description=LocalizedDesc(english_us="Add a self role to a message", french="Ajoute un self role à un message")
    )
    @interactions.slash_option(
        name="message_id",
        description=LocalizedDesc(english_us="Message ID", french="ID du message"),
        opt_type=interactions.OptionType.STRING,
        required=True
    )
    @interactions.slash_option(
        name="emoji",
        description="Emoji",
        opt_type=interactions.OptionType.STRING,
        required=True
    )
    @interactions.slash_option(
        name="role",
        description=LocalizedDesc(english_us="Role to add", french="Role à ajouter"),
        opt_type=interactions.OptionType.ROLE,
        required=True
    )
    async def self_role(self, ctx: interactions.SlashContext, message_id: str, emoji: str, role: interactions.Role):
        if await database_exists(ctx) is not True:
            return
        if await is_admin(ctx) is not True:
            return

        test = [message.id async for message in ctx.channel.history(limit=100)]

        message = self.bot.get_channel(ctx.channel.id).get_message(message_id)

        if int(message_id) not in test:
            return await ctx.send(ErrorMessage.MessageNotFound(ctx.guild.id, message_id), ephemeral=True)

        conn = sqlite3.connect(f'./Database/{ctx.guild.id}.db')
        c = conn.cursor()

        c.execute(f"INSERT INTO self_role VALUES ('{message_id}', '{emoji}', '{role.id}')")
        conn.commit()
        conn.close()

        await message.add_reaction(emoji)
        await ctx.send(f"L'émoji {emoji} a bien été ajouté au message `{message.id}` !", ephemeral=True)

    @interactions.listen(MessageReactionAdd)
    async def on_message_reaction_add(self, reaction: interactions.events.MessageReactionAdd):
        if reaction.author.bot:
            return

        if await database_exists(reaction) is not True:
            return

        conn = sqlite3.connect(f'./Database/{reaction.message.guild.id}.db')
        c = conn.cursor()

        message_id = c.execute(f"SELECT message_id FROM self_role WHERE message_id = {reaction.message.id}").fetchone()
        if message_id is None:
            return

        emoji = c.execute(f"SELECT emoji FROM self_role WHERE message_id = {reaction.message.id}").fetchone()[0]
        role_id = c.execute(f"SELECT role_id FROM self_role WHERE message_id = {reaction.message.id}").fetchone()[0]

        partial_emoji = interactions.PartialEmoji.from_str(emoji)
        discord_partial_emoji = interactions.PartialEmoji.from_str(str(reaction.emoji))

        if reaction.message.id == message_id[0]:
            if discord_partial_emoji == partial_emoji:
                message = self.bot.get_channel(reaction.reaction.channel.id).get_message(reaction.message.id)
                user = self.bot.get_user(reaction.author.id)
                guild = self.bot.get_guild(reaction.message.guild.id)
                role = guild.get_role(role_id)

                await message.remove_reaction(emoji, reaction.author)

                if role in reaction.author.roles:
                    await reaction.author.remove_role(role)
                    return await user.send(f"Le role **{role.name}** a bien été retiré sur le serveur **{guild.name}** !")
                else:
                    await reaction.author.add_role(role)
                    return await user.send(f"Le role **{role.name}** a bien été ajouté sur le serveur **{guild.name}** !")
        else:
            return


def setup(bot):
    SelfRole(bot)
