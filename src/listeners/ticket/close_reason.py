import asyncio
import io
import sqlite3
import interactions
from interactions.ext.transcript import get_transcript
from datetime import datetime
from message_config import ErrorMessage


class CloseReasonTicket(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("close_reason_ticket")
    async def button_close_reason(self, ctx):
        guild = await ctx.get_guild()
        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()
        if c.execute("SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0] in ctx.author.roles or c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles:
            conn.close()

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
            conn.close()
            await ctx.send(ErrorMessage.MissingPermissions(guild.id), ephemeral=True)

    @interactions.extension_modal("close_reason")
    async def on_modal_finish(self, ctx, reason: str):
        channel = await ctx.get_channel()
        guild = await ctx.get_guild()

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        # Partie Database
        c.execute(f'SELECT * from ticket WHERE channel_id = {int(channel.id)}')
        result = c.fetchone()

        c.execute("UPDATE ticket_count SET count = count+1 WHERE user_id = '{}'".format(result[1]))
        conn.commit()

        # Partie transcript
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

        # Partie logs
        logs = await interactions.get(self.bot, interactions.Channel, object_id=c.execute("SELECT id FROM logs_channels WHERE name = 'close'").fetchone()[0])
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
        em3.add_field(name="__**Fermé par**__", value=ctx.author.mention, inline=True)
        if row[2] != "None":
            em3.add_field(name="__**Claim par**__", value=f"<@{row[2]}>", inline=True)
        em3.add_field(name="__**Raison**__", value=reason, inline=True)

        await logs.send(embeds=em3, files=file)

        conn.close()


def setup(bot):
    CloseReasonTicket(bot)
