import sqlite3
import io
import asyncio
import interactions
from interactions.ext.transcript import get_transcript
from datetime import datetime

from const import DATA


class ConfirmClose(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("confirm_close")
    async def confirm_close_button(self, ctx):
        # Partie Database
        conn = sqlite3.connect('./Database/puwlerson.db')
        c = conn.cursor()

        # Partie transcript
        channel = await ctx.get_channel()
        transcript = await get_transcript(channel=channel, mode="plain")
        file = interactions.File(filename="transcript.txt", fp=io.StringIO(transcript))

        em2 = interactions.Embed(
            description="Transcript effectué.",
            color=0x00FF00
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

        logs = await interactions.get(self.bot, interactions.Channel, object_id=DATA["logs"]["ticket"]["close"])
        c.execute(f'SELECT * from ticket WHERE channel_id = {int(channel.id)}')
        row = c.fetchone()
        em3 = interactions.Embed(
            title="Fermeture de ticket",
            description="Un ticket a été fermé.",
            color=0xFF4646,
            timestamp=datetime.utcnow()
        )
        em3.add_field(name="__**Ticket ID**__", value=row[0], inline=True)
        em3.add_field(name="__**Ouvert par**__", value=f"<@{row[1]}>", inline=True)
        em3.add_field(name="__**Fermé par**__", value=ctx.author.mention, inline=True)
        if row[2] != "None":
            em3.add_field(name="__**Claim par**__", value=f"<@{row[2]}>", inline=True)
        em3.add_field(name="__**Raison**__", value="Aucune raison fournie", inline=True)

        await logs.send(embeds=em3, files=file)

        conn.close()


def setup(bot):
    ConfirmClose(bot)
