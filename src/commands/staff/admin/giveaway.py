import asyncio
import os
import sqlite3
import interactions
from interactions import LocalizedName, LocalizedDesc
from random import choice
from time import time

from src.utils.checks import database_exists, is_admin, is_plugin
from src.utils.message_config import ErrorMessage
from src.utils.time_converter import readable_to_time


class Giveaway(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.button = interactions.Button(
            label="Participer",
            style=interactions.ButtonStyle.SUCCESS,
            custom_id="giveaway"
        )
        self.dict = {}
        self.check = False

    @interactions.slash_command(
        description=LocalizedDesc(english_us="Start a giveaway", french="Lance un giveaway"),
        dm_permission=False
    )
    @interactions.slash_option(
        name=LocalizedName(english_us="prize", french="gain"),
        description=LocalizedDesc(english_us="What is the prize ?", french="Quel est le gain ?"),
        opt_type=interactions.OptionType.STRING,
        required=True
    )
    @interactions.slash_option(
        name=LocalizedName(english_us="duration", french="durée"),
        description=LocalizedDesc(english_us="How long will the giveaway last ?",
                                  french="Combien de temps va durer le giveaway ?"),
        opt_type=interactions.OptionType.STRING,
        required=True
    )
    @interactions.slash_option(
        name=LocalizedName(english_us="winners", french="gagnants"),
        description=LocalizedDesc(english_us="How many winners ? (Default : 1)",
                                  french="Combien de gagnants ? (Par défaut : 1)"),
        opt_type=interactions.OptionType.INTEGER,
        required=False
    )
    async def giveaway(self, ctx: interactions.SlashContext, prize: str, duration: str, winners: int = 1):
        if await database_exists(ctx) is not True:
            return

        if await is_admin(ctx) is not True:
            return

        if is_plugin(ctx, "giveaway") is not True:
            return

        guild = ctx.guild

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        # Check si un giveaway est déjà en cours
        if self.check:
            return await ctx.send(ErrorMessage.giveaway_already_started(guild.id), ephemeral=True)

        time_to_wait = readable_to_time(duration[:-1], duration[-1])

        timestamp = time() + time_to_wait
        channel = self.bot.get_channel(c.execute("SELECT id FROM channels WHERE type = 'Giveaway'").fetchone()[0])

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
        await asyncio.sleep(time_to_wait)

        winner = []
        for _ in range(winners):
            winner_choice = choice(list(self.dict.keys()))
            if winner_choice not in winner:
                winner.append(winner_choice)

        user = [await interactions.get(self.bot, interactions.User, object_id=winner[i]) for i in
                range(len(winner))]

        em_end = interactions.Embed(
            title="Nouveau Giveaway ! 🎊",
            description=f"Le giveaway lancé par {ctx.author.mention} est terminé ! ",
            color=0x75FD75
        )
        em_end.add_field(name="Gain", value=prize, inline=True)
        if winners == 1:
            em_end.add_field(name="Gagnant", value=user[0].mention, inline=True)
        else:
            em_end.add_field(name="Gagnant", value=", ".join([user[i].mention for i in range(len(user))]),
                             inline=True)
        em_end.add_field(name="Nombre de participants", value=len(self.dict), inline=True)

        await message.edit(embeds=em_end, components=[])

        if winners == 1:
            await channel.send(f"Le giveaway est terminé ! Le gagnant est {user[0].mention} !")
        else:
            await channel.send(
                f"Le giveaway est terminé ! Les gagnants sont {', '.join([user[i].mention for i in range(len(user))])} !")

        channel = self.bot.get_channel(
            c.execute("SELECT id FROM logs_channels WHERE name = 'giveaway'").fetchone()[0])

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
        em.add_field(name="Nombre de participants", value=len(self.dict), inline=True)
        await channel.send(embeds=em)

        self.dict.clear()
        self.check = False

        conn.close()

    @interactions.component_callback("giveaway")
    async def on_button_click(self, ctx: interactions.ComponentContext):
        """Permet de participer au giveaway."""
        guild = ctx.guild
        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles or \
                c.execute("SELECT id FROM roles WHERE type = 'Admin'").fetchone()[0] in ctx.author.roles:
            conn.close()
            return await ctx.send("Vous ne pouvez pas participer au giveaway !", ephemeral=True)
        if ctx.author.id not in self.dict:
            conn.close()
            self.dict[ctx.author.id] = 1
            return await ctx.send(f"Vous participez désormais au giveaway !", ephemeral=True)
        else:
            conn.close()
            self.dict.pop(ctx.author.id)
            return await ctx.send(f"Vous ne participez plus au giveaway !", ephemeral=True)


def setup(bot):
    Giveaway(bot)
