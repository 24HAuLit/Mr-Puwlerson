import sqlite3
import interactions
from interactions import LocalizedDesc
from src.commands.ticket.tickets import Tickets
from src.utils.checks import is_staff, database_exists, ticket_parent


class ClaimCommand(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @Tickets.ticket.subcommand(
        sub_cmd_name="claim",
        sub_cmd_description=LocalizedDesc(english_us="To claim a ticket", french="Pour revendiquer un ticket",
                                          default_locale="english_us")
    )
    async def claim(self, ctx: interactions.SlashContext):
        if await database_exists(ctx) is not True:
            return

        if await is_staff(ctx) is not True:
            return

        if await ticket_parent(ctx) is not True:
            return

        guild = ctx.guild

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        channel = ctx.channel
        id_staff = ctx.author.id

        # Partie Database
        c.execute(f'SELECT * from ticket WHERE channel_id = {int(channel.id)}')
        row = c.fetchone()

        # Partie commande
        if row[2] is None or row[2] == 'None':
            c.execute(f"UPDATE ticket SET staff_id = {id_staff} WHERE channel_id = {int(channel.id)}")

            conn.commit()
            em = interactions.Embed(
                description=f"Le ticket a été pris en charge par {ctx.author.mention}.",
                color=0x2ECC70
            )
            await ctx.send(embeds=em)
        elif row[2] == id_staff:
            await ctx.send(f"Vous avez déjà pris en charge ce ticket.", ephemeral=True)
        else:
            await ctx.send(f"<@{row[2]}> a déjà pris en charge ce ticket.", ephemeral=True)

        return conn.close()

    @Tickets.ticket.subcommand(
        sub_cmd_name="unclaim",
        sub_cmd_description=LocalizedDesc(english_us="To unclaim a ticket", french="Pour dé-revendiquer un ticket",
                                          default_locale="english_us")
    )
    async def unclaim(self, ctx: interactions.SlashContext):

        if await database_exists(ctx) is not True:
            return

        if await is_staff(ctx) is not True:
            return

        if await ticket_parent(ctx) is not True:
            return

        guild = ctx.guild

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        channel = ctx.channel
        id_staff = ctx.author.id

        # Partie Database
        c.execute(f'SELECT * from ticket WHERE channel_id = {int(channel.id)}')
        row = c.fetchone()

        # Partie commande
        if row[2] == id_staff:
            c.execute(f"UPDATE ticket SET staff_id = 'None' WHERE channel_id = {int(channel.id)}")

            conn.commit()
            em = interactions.Embed(
                description=f"Le ticket n'est plus pris en charge par {ctx.author.mention}.",
                color=0x2ECC70
            )
            await ctx.send(embeds=em)
        elif row[2] is None or row[2] == 'None':
            await ctx.send(f"Personne ne prend en charge ce ticket.", ephemeral=True)
        else:
            await ctx.send(f"Vous ne pouvez pas faire ceci car <@{row[2]}> a pris ce ticket.", ephemeral=True)

        return conn.close()


def setup(bot):
    ClaimCommand(bot)
