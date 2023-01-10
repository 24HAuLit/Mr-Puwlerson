import asyncio
import io
import sqlite3
import interactions
from interactions.ext.transcript import get_transcript
from datetime import datetime
from const import DATA


class CloseReasonTicket(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("close_reason_ticket")
    async def button_close_reason(self, ctx):
        if DATA["roles"]["Staff"] in ctx.author.roles or DATA["roles"]["Owner"] in ctx.author.roles:
            modal = interactions.Modal(
                title="Raison",
                custom_id="close_reason",
                components=[
                    interactions.TextInput(
                        style=interactions.TextStyleType.SHORT,
                        label="Pourquoi fermer ce ticket ?",
                        custom_id="text_input_question_response",
                        min_length=1,
                        max_length=500
                    )
                ]
            )
            await ctx.popup(modal)
        else:
            await ctx.send(":x: Vous n'avez pas la permission de faire ceci.", ephemeral=True)

    @interactions.extension_modal("close_reason")
    async def on_modal_finish(self, _ctx, reason: str):
        # Partie transcript
        channel = await _ctx.get_channel()
        transcript = await get_transcript(channel=channel, mode="plain")
        file = interactions.File(filename="transcript.txt", fp=io.StringIO(transcript))

        em2 = interactions.Embed(
            description="Transcript effectué.",
            color=0x00FF00
        )
        await _ctx.send(embeds=em2)

        # Partie suppression
        em = interactions.Embed(
            description="Ce ticket va être fermé dans quelques instant...",
            color=0xFF0000
        )
        await _ctx.send(embeds=em)
        await asyncio.sleep(5)
        await _ctx.channel.delete()

        # Partie logs
        conn = sqlite3.connect('./Database/puwlerson.db')
        c = conn.cursor()
        logs = await interactions.get(self.bot, interactions.Channel, object_id=DATA["logs"]["ticket"]["close"])
        c.execute(f'SELECT * FROM ticket WHERE channel_id = {int(channel.id)}')
        row = c.fetchone()
        em3 = interactions.Embed(
            title="Fermeture de ticket",
            description="Un ticket a été fermé.",
            color=0xFF4646,
            timestamp=datetime.utcnow()
        )
        em3.add_field(name="__**Ticket ID**__", value=row[0], inline=True)
        em3.add_field(name="__**Ouvert par**__", value=f"<@{row[1]}>", inline=True)
        em3.add_field(name="__**Fermé par**__", value=_ctx.author.mention, inline=True)
        if row[2] != "None":
            em3.add_field(name="__**Claim par**__", value=f"<@{row[2]}>", inline=True)
        em3.add_field(name="__**Raison**__", value=reason, inline=True)

        await logs.send(embeds=em3, files=file)

        conn.close()


def setup(bot):
    CloseReasonTicket(bot)
