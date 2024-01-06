import asyncio
import io
import sqlite3
import interactions
from interactions import Extension, Client, LocalizedName, LocalizedDesc, SlashContext
from interactions.ext.transcript import get_transcript
from src.listeners.ticket.components.close import confirm_close_cmd
from src.commands.ticket.tickets import Tickets
from src.utils.checks import is_staff, database_exists, ticket_parent


class CloseTicketCommand(Extension):

    def __init__(self, bot):
        self.bot: Client = bot
        self.reason = None

    @Tickets.ticket.subcommand(
        sub_cmd_name="close",
        sub_cmd_description=LocalizedDesc(english_us="To close a ticket", french="Pour fermer un ticket"),
    )
    @interactions.slash_option(
        name=LocalizedName(english_us="reason", french="raison"),
        description=LocalizedDesc(english_us="Reason to close", french="Raison de la fermeture"),
        opt_type=interactions.OptionType.STRING,
        required=False
    )
    async def close(self, ctx: SlashContext, reason: str = "Aucune raison."):
        if await database_exists(ctx) is not True:
            return

        if await is_staff(ctx) is not True:
            return

        if await ticket_parent(ctx) is not True:
            return

        self.reason = reason
        await ctx.send("Êtes-vous sur de vouloir fermer ce ticket ?", components=confirm_close_cmd(), ephemeral=True)

    @interactions.component_callback("confirm_close_cmd")
    async def confirm_close(self, ctx: interactions.ComponentContext):
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
        em3.add_field(name="__**Raison**__", value=self.reason, inline=True)

        await logs.send(
            embeds=em3,
            # files=file
        )

        conn.close()


def setup(bot):
    CloseTicketCommand(bot)
