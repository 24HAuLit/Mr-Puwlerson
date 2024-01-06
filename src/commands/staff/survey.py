import asyncio
import os
import sqlite3
import interactions
from src.utils.message_config import ErrorMessage


class Survey(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    @interactions.option(description="Quelle sera la question ?", required=True)
    @interactions.option(description="Quels choix (10 max) ? Les séparés avec ;", required=True)
    async def survey(self, ctx: interactions.CommandContext, question: str, choices: str):
        guild = await ctx.get_guild()

        if os.path.exists(f"./Database/{guild.id}.db") is False:
            return await ctx.send(ErrorMessage.database_not_found(guild.id), ephemeral=True)

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if c.execute("SELECT id FROM roles WHERE type = 'Admin'").fetchone()[0] in ctx.author.roles or \
                c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles:
            emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", '8️⃣', "9️⃣", "🔟"]
            choices = choices.split(";")

            if len(choices) > 10:
                return await ctx.send("Vous ne pouvez pas mettre plus de 10 choix !", ephemeral=True)

            for i in range(len(choices)):
                choices[i] = emojis[i] + " " + choices[i]

            em = interactions.Embed(
                title="Nouveau sondage",
                description=f"**{question}**",
                color=0x00FFC8
            )
            em.add_field(name="Choix", value="\n".join(choices))
            if ctx.author.discriminator == "0":
                em.set_footer(text=f"Sondage crée par {ctx.author.username}", icon_url=ctx.author.avatar_url)
            else:
                em.set_footer(text=f"Sondage crée par {ctx.author.username}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
            message = await ctx.send(embeds=em)

            for i in range(len(choices)):
                await message.create_reaction(emojis[i])
                await asyncio.sleep(0.5)

        else:
            await ctx.send(ErrorMessage.MissingPermissions(guild.id), ephemeral=True)
            return interactions.StopCommand()


def setup(bot):
    Survey(bot)
