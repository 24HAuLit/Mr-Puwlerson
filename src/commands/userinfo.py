from datetime import datetime

import interactions


class UserInfo(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command(
        name="userinfo",
        description="Permet d'obtenir les informations d'un utilisateur"
    )
    @interactions.option(
        name="user",
        description="Utilisateur dont tu veux les infos",
        type=interactions.OptionType.USER,
        required=False
    )
    async def userinfo(self, ctx: interactions.CommandContext, user=None):
        if user is None:
            user = ctx.author

        em = interactions.Embed(
            description=f"Informations sur {user.mention} :",
            color=0x303434,
            timestamp=datetime.utcnow()
        )
        em.set_author(name=f"{user.username}#{user.discriminator}")
        em.set_thumbnail(url=user.get_avatar_url())
        em.add_field(name="**Identifiant**", value=str(user.id), inline=True)
        em.add_field(name="**Pseudo**", value=user.name, inline=True)
        await ctx.send(embeds=em, ephemeral=True)


def setup(bot):
    UserInfo(bot)
