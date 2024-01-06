import asyncio
import sqlite3
import interactions
from src.utils.checks import is_staff, database_exists


class CloseReasonTicket(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.component_callback("close_reason_ticket")
    async def button_close_reason(self, ctx: interactions.ComponentContext):
        if await database_exists(ctx) is not True:
            return

        if await is_staff(ctx) is not True:
            return

        modal = interactions.Modal(
            interactions.ParagraphText(
                label="Raison",
                placeholder="Raison de la fermeture du ticket",
                custom_id="short_response",
                min_length=1,
                max_length=512
            ),
            title="Raison",
            custom_id="close_reason",
        )

        await ctx.send_modal(modal)

    @interactions.modal_callback("close_reason")
    async def on_modal_finish(self, ctx: interactions.ModalContext, short_response: str):
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

        # Partie logs
        logs = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'close'").fetchone()[0])
        c.execute(f'SELECT * FROM ticket WHERE channel_id = {int(channel.id)}')
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
        em3.add_field(name="__**Raison**__", value=short_response, inline=True)

        await logs.send(
            embeds=em3,
            # files=file
        )

        conn.close()
