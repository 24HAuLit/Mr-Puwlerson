import asyncio
import sqlite3
import interactions
from interactions import LocalizedDesc
from src.utils.checks import database_exists, is_admin
from src.utils.message_config import ErrorMessage


class Nuke(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

        self.confirm_button = interactions.Button(
            style=interactions.ButtonStyle.DANGER,
            label="Confirmer",
            emoji="💥",
            custom_id="confirm",
            disabled=False
        )

        self.refused_button = interactions.Button(
            style=interactions.ButtonStyle.SUCCESS,
            label="Refuser",
            emoji="🤔",
            custom_id="refused"
        )

        self.message = None

    @interactions.slash_command(
        description=LocalizedDesc(english_us="Destroy the channel like Nuketown in Black Ops 1.",
                                  french="Détruit le channel tah Nuketown sur Black Ops 1."),
        dm_permission=False
    )
    async def nuke(self, ctx: interactions.SlashContext):
        if await database_exists(ctx) is not True:
            return

        if await is_admin(ctx) is False:
            return await ctx.send(ErrorMessage.MissingPermissions(ctx.guild.id), ephemeral=True)

        await ctx.send("Voulez-vous vraiment détruire ce salon ? **Cette action est irréversible.**",
                       components=[self.confirm_button, self.refused_button], ephemeral=True)

    @interactions.component_callback("confirm")
    async def confirm(self, ctx: interactions.ComponentContext):
        actual = ctx.channel
        new = await actual.clone()

        await ctx.edit_origin(content="Vous avez confirmé la destruction de ce salon", components=[])

        count = 5
        embed1 = interactions.Embed(description=f"Ce salon va disparaitre dans **{count}** secondes.",
                                    color=0xFF0000,
                                    timestamp=interactions.Timestamp.utcnow())
        embed1.set_footer(icon_url=ctx.member.user.avatar.url, text=f"Commande demandé par {ctx.author.username}.")

        warning_message = await actual.send(embeds=embed1)

        for i in range(5):
            embed2 = interactions.Embed(description=f"Ce salon va disparaitre dans **{count}** secondes.",
                                        color=0xFF0000,
                                        timestamp=interactions.Timestamp.utcnow())
            embed2.set_footer(icon_url=ctx.member.user.avatar.url, text=f"Commande demandé par {ctx.author.username}.")
            count -= 1
            await warning_message.edit(embeds=embed2)
            await asyncio.sleep(1)

        await ctx.channel.delete(reason="Nuked")

        embed3 = interactions.Embed(description="Salon tout neuf, rien que pour vous.", color=0x75FF75,
                                    timestamp=interactions.Timestamp.utcnow())

        await new.send(embeds=embed3)

        # Partie Logs
        guild = ctx.guild
        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        logs_nuke = self.bot.get_channel(
            c.execute("SELECT id FROM logs_channels WHERE name = 'nuke'").fetchone()[0])

        conn.close()

        em2 = interactions.Embed(title="**💣 Nouveau nuke**", description=f"Un channel a été nuke.",
                                 color=0xFF0000,
                                 timestamp=interactions.Timestamp.utcnow())
        em2.add_field(name="**Ancien channel : **", value=f"Nom : {actual.name} | ID : {actual.id}")
        em2.add_field(name="**Nouveau channel : **", value=f"Nom : {new.name} ({new.mention}) | ID : {new.id}")
        em2.set_footer(icon_url=ctx.member.user.avatar.url,
                       text=f"Author ID : {ctx.author.id} | Name : {ctx.author.username}.")

        await logs_nuke.send(embeds=em2)

    @interactions.component_callback("refused")
    async def refused(self, ctx: interactions.ComponentContext):
        await ctx.edit_origin(content="Vous avez annulé la destruction de ce salon.", components=[])


def setup(bot):
    Nuke(bot)
