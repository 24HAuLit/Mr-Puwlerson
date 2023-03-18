import asyncio
import os
import sqlite3
import interactions
from random import choice
from time import time
from const import DATA
from message_config import ErrorMessage


class Giveaway(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.button = interactions.Button(
            label="Participer",
            style=interactions.ButtonStyle.SUCCESS,
            custom_id="giveaway"
        )
        self.dic = {}
        self.check = False

    @interactions.extension_command(dm_permission=False)
    @interactions.option(description="Quel sera le cadeau ?")
    @interactions.option(description="Combien de temps durera le giveaway ? (en secondes)")
    @interactions.option(description="Nombre de gagnants ?", required=False)
    async def giveaway(self, ctx: interactions.CommandContext, prize: str, seconds: int, winners: int = 1):
        """Crée un giveaway."""
        guild = await ctx.get_guild()

        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return await ctx.send(ErrorMessage.database_not_found(guild.id), ephemeral=True)

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if c.execute("SELECT status FROM plugins WHERE name = 'giveaway'").fetchone()[0] == "false":
            return await ctx.send(ErrorMessage.PluginError(guild.id, "giveaway"), ephemeral=True)

        # Permission check
        if c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles or \
                c.execute("SELECT id FROM roles WHERE type = 'Admin'").fetchone()[0] in ctx.author.roles:
            # Check si un giveaway est déjà en cours
            if self.check:
                return await ctx.send(ErrorMessage.giveaway_already_started(guild.id), ephemeral=True)

            timestamp = time() + seconds
            channel = await interactions.get(self.bot, interactions.Channel, object_id=DATA["main"]["giveaway"])

            # Giveaway starting
            self.check = True
            em = interactions.Embed(
                title="Nouveau Giveaway ! 🎊",
                description=f"Un giveaway a été lancé par {ctx.author.mention} !\n*Cliquez sur le bouton ci-dessous pour participer.*",
                color=0x00FFC8
            )
            em.add_field(name="Gain", value=prize)
            em.add_field(name="Nombre de gagnants", value=winners)
            em.add_field(name="Date de fin", value=f"<t:{int(timestamp)}:R>")
            await ctx.send("Le giveaway a bien été lancé !", ephemeral=True)
            message = await channel.send(embeds=em, components=[self.button])

            # Giveaway ending
            await asyncio.sleep(seconds)

            winner = []
            for _ in range(winners):
                winner_choice = choice(list(self.dic.keys()))
                if winner_choice not in winner:
                    winner.append(winner_choice)

            user = [await interactions.get(self.bot, interactions.User, object_id=winner[i]) for i in range(len(winner))]

            em_end = interactions.Embed(
                title="Nouveau Giveaway ! 🎊",
                description=f"Le giveaway lancé par {ctx.author.mention} est terminé ! ",
                color=0x75FD75
            )
            em_end.add_field(name="Gain", value=prize, inline=True)
            if winners == 1:
                em_end.add_field(name="Gagnant", value=user[0].mention, inline=True)
            else:
                em_end.add_field(name="Gagnant", value=", ".join([user[i].mention for i in range(len(user))]), inline=True)
            em_end.add_field(name="Nombre de participants", value=len(self.dic), inline=True)

            await message.edit(embeds=em_end, components=[])

            if winners == 1:
                await channel.send(f"Le giveaway est terminé ! Le gagnant est {user[0].mention} !")
            else:
                await channel.send(f"Le giveaway est terminé ! Les gagnants sont {', '.join([user[i].mention for i in range(len(user))])} !")

            logs_id = c.execute("SELECT id FROM logs_channels WHERE name = 'giveaway'").fetchone()[0]
            channel = await interactions.get(self.bot, interactions.Channel, object_id=logs_id)

            em = interactions.Embed(
                title="🎊・Giveaway",
                description=f"Le giveaway lancé par {ctx.author.mention} est terminé !",
                color=0x75FD75
            )
            em.add_field(name="Gain", value=prize, inline=True)
            if winners == 1:
                em.add_field(name="Gagnant", value=user[0].mention, inline=True)
            else:
                em.add_field(name="Gagnant", value=", ".join([user[i].mention for i in range(len(user))]), inline=True)
            em.add_field(name="Nombre de participants", value=len(self.dic), inline=True)
            await channel.send(embeds=em)

            self.dic.clear()
            self.check = False
        else:
            await ctx.send(ErrorMessage.MissingPermissions(guild.id), ephemeral=True)
            return interactions.StopCommand()

        conn.close()

    @interactions.extension_component("giveaway")
    async def on_button_click(self, ctx: interactions.ComponentContext):
        """Permet de participer au giveaway."""
        guild = await ctx.get_guild()
        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles or \
                c.execute("SELECT id FROM roles WHERE type = 'Admin'").fetchone()[0] in ctx.author.roles:
            conn.close()
            return await ctx.send("Vous ne pouvez pas participer au giveaway !", ephemeral=True)
        if ctx.author.id not in self.dic:
            conn.close()
            self.dic[ctx.author.id] = 1
            return await ctx.send(f"Vous participez désormais au giveaway !", ephemeral=True)
        else:
            conn.close()
            self.dic.pop(ctx.author.id)
            return await ctx.send(f"Vous ne participez plus au giveaway !", ephemeral=True)


def setup(bot):
    Giveaway(bot)
