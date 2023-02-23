import asyncio
import os
import sqlite3

import interactions
from datetime import datetime
from const import DATA


class Nuke(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    confirm_button = interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="Confirmer",
        custom_id="confirm"
    )

    refused_button = interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="Refuser",
        custom_id="refused"
    )

    @interactions.extension_command(dm_permission=False)
    async def nuke(self, ctx: interactions.CommandContext):
        """Détruis le channel tah Nuketown sur Black Ops 1."""
        guild = await ctx.get_guild()

        if os.path.exists(f"./Database/{guild.id}.db") is False:
            return await ctx.send("Ce serveur n'est pas encore configuré.", ephemeral=True)

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles or \
                c.execute("SELECT id FROM roles WHERE type = 'Admin'").fetchone()[0] in ctx.author.roles:
            await ctx.send("Voulez-vous vraiment détruire ce salon ? **Cette action est irréversible.**",
                           components=[self.confirm_button, self.refused_button], ephemeral=True)
        else:
            await ctx.send(":x: Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            interactions.StopCommand()

        conn.close()
        try:
            await self.bot.wait_for_component(
                components=[self.confirm_button, self.refused_button], check=[self.button_confirm, self.button_refuse],
                timeout=15
            )
            pass
        except asyncio.TimeoutError:
            await ctx.edit(components=[])
            return interactions.StopCommand()

    @interactions.extension_component("confirm")
    async def button_confirm(self, ctx):
        actual = await ctx.get_channel()
        new = await ctx.guild.clone_channel(actual)
        await ctx.edit(components=[])
        await ctx.send("Vous avez confirmé la destruction de ce salon.", ephemeral=True)

        count = 5
        embed1 = interactions.Embed(description=f"Ce salon va disparaitre dans **{count}** secondes.",
                                    color=0xFF0000,
                                    timestamp=datetime.utcnow())
        embed1.set_footer(icon_url=ctx.member.user.avatar_url, text=f"Commande demandé par {ctx.author}.")
        await ctx.send(embeds=embed1)

        for i in range(5):
            embed2 = interactions.Embed(description=f"Ce salon va disparaitre dans **{count}** secondes.",
                                        color=0xFF0000,
                                        timestamp=datetime.utcnow())
            embed2.set_footer(icon_url=ctx.member.user.avatar_url, text=f"Commande demandé par {ctx.author}.")
            count -= 1
            await ctx.message.edit(embeds=embed2)
            await asyncio.sleep(1)

        await ctx.channel.delete()

        embed3 = interactions.Embed(description="Salon tout neuf, rien que pour vous.", color=0x75FF75,
                                    timestamp=datetime.utcnow())
        await new.send(embeds=embed3)

        # Partie Logs
        logs_nuke = await interactions.get(self.bot, interactions.Channel, object_id=c.execute("SELECT id FROM logs_channels WHERE name = 'blacklist'").fetchone()[0])

        em2 = interactions.Embed(title="**💣 Nouveau nuke**", description=f"Un channel a été nuke.",
                                 color=0xFF0000,
                                 timestamp=datetime.utcnow())
        em2.add_field(name="**Ancien channel : **", value=f"Nom : {actual} | ID : {actual.id}")
        em2.add_field(name="**Nouveau channel : **", value=f"Nom : {new} ({new.mention}) | ID : {new.id}")
        em2.set_footer(icon_url=ctx.member.user.avatar_url, text=f"Author ID : {ctx.author.id} | Name : {ctx.author}.")

        await logs_nuke.send(embeds=em2)

    @interactions.extension_component("refused")
    async def button_refuse(self, ctx):
        await ctx.edit(components=[])
        await ctx.send("Vous avez annulé la destruction de ce salon.", ephemeral=True)


def setup(bot):
    Nuke(bot)
