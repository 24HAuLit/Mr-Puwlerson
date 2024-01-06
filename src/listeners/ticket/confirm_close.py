import sqlite3
import io
import asyncio
import interactions
from interactions.ext.transcript import get_transcript


class ConfirmClose(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.component_callback("confirm_close")
    async def confirm_close_button(self, ctx: interactions.ComponentContext):
        channel = ctx.channel
        guild = ctx.guild

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        # Partie Database
        c.execute(f'SELECT * from ticket WHERE channel_id = {int(channel.id)}')
        result = c.fetchone()

        c.execute("UPDATE ticket_count SET count = count+1 WHERE user_id = '{}'".format(result[1]))
        conn.commit()

        # Partie transcript // HS pour l'instant
        # transcript = await get_transcript(channel=channel, mode="plain")
        # file = interactions.File(filename="transcript.txt", fp=io.StringIO(transcript))
        #
        # em2 = interactions.Embed(
        #     description="Transcript effectué.",
        #     color=0x00FF00
        # )
        # await ctx.send(embeds=em2)

        em2 = interactions.Embed(
            description="**Transcript HS** pour une durée indéterminée.",
            color=0xFF0000
        )
        await ctx.send(embeds=em2)

        # Partie suppression
        em = interactions.Embed(
            description="Ce ticket va être fermé dans quelques instant...",
            color=0xFF0000
        )
        await ctx.send(embeds=em)
        await asyncio.sleep(5)
        await ctx.channel.delete()

        # Partie Logs

        logs = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'close'").fetchone()[0])
        c.execute(f'SELECT * from ticket WHERE channel_id = {int(channel.id)}')
        row = c.fetchone()
        em3 = interactions.Embed(
            title="Fermeture de ticket",
            description="Un ticket a été fermé.",
            color=0xFF4646,
            timestamp=interactions.Timestamp.utcnow()
        )
        em3.add_field(name="__**Ticket ID**__", value=row[0], inline=True)
        em3.add_field(name="__**Ouvert par**__", value=f"<@{row[1]}>", inline=True)
        em3.add_field(name="__**Fermé par**__", value=ctx.author.mention, inline=True)
        if row[2] != "None":
            em3.add_field(name="__**Claim par**__", value=f"<@{row[2]}>", inline=True)
        em3.add_field(name="__**Raison**__", value="Aucune raison fournie", inline=True)

        await logs.send(
            embeds=em3,
            # files=file
        )

        conn.close()
