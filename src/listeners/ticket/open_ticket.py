import sqlite3
import interactions
from src.listeners.ticket.components.claim import ticket_claim
from src.listeners.ticket.components.close import ticket_close_reason, ticket_close
from src.utils.checks import database_exists, is_staff
from src.utils.message_config import ErrorMessage


class OpenTicket(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.component_callback("open_ticket")
    async def button_open(self, ctx: interactions.ComponentContext):
        guild = ctx.guild
        author_id = ctx.author.id

        if await database_exists(ctx) is not True:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        # Partie vérification limite de ticket
        c.execute(f"SELECT count FROM ticket_count WHERE user_id = {int(ctx.author.id)}")
        count = c.fetchone()

        if await is_staff(ctx) is not True:
            if count is not None and count[0] == 0:
                return await ctx.send(ErrorMessage.ticket_limit(guild.id), ephemeral=True)

            c.execute(
                """INSERT OR REPLACE INTO ticket_count (user_id, count) VALUES (?, COALESCE((SELECT count FROM 
                ticket_count WHERE user_id=?), 0) - 1)""",
                (int(ctx.author.id), int(ctx.author.id)))
            conn.commit()

        # Partie création ticket
        channel = await guild.create_text_channel(
            name=f"ticket-{ctx.user.username}",
            category=c.execute("SELECT id FROM channels WHERE type = 'ticket_parent'").fetchone()[0],
            permission_overwrites=[
                interactions.PermissionOverwrite(
                    id=c.execute("SELECT id FROM roles WHERE name = '@everyone'").fetchone()[0],
                    type=0, deny=2199023255551),
                interactions.PermissionOverwrite(id=int(ctx.author.id), type=1,
                                                 allow=64 | 1024 | 2048 | 32768 | 65536 | 262144 | 2147483648),
                interactions.PermissionOverwrite(
                    id=c.execute("SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0], type=0,
                    allow=64 | 1024 | 2048 | 8192 | 32768 | 65536 | 262144 | 2147483648)
            ]
        )
        await ctx.send(f"Votre ticket a été créé {channel.mention}", ephemeral=True)

        c.execute("INSERT INTO ticket VALUES (NULL, '{}', '{}', '{}')".format(author_id, None, channel.id))
        conn.commit()

        em = interactions.Embed(
            title="Nouveau ticket",
            description="Votre ticket a été ouvert.\n**Un Staff vous répondra sous peu.** Il est inutile de ping les staffs.",
            color=0x2ECC70,
            timestamp=interactions.Timestamp.utcnow()
        )
        em.set_footer(text=f"Author ID : {ctx.author.id} | Ticket ID : {c.lastrowid}")
        message = await channel.send(embeds=em, components=[ticket_close(), ticket_close_reason(), ticket_claim()])
        await message.pin()

        # Partie Logs
        channel_logs = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'create'").fetchone()[0])

        if ctx.author.discriminator == "0":
            em2 = interactions.Embed(
                title="Nouveau ticket",
                description=f"**{ctx.author.username}** a crée un nouveau ticket (**{channel.name}**).",
                color=0x2ECC70,
                timestamp=interactions.Timestamp.utcnow()
            )
        else:
            em2 = interactions.Embed(
                title="Nouveau ticket",
                description=f"**{ctx.author.username}#{ctx.author.discriminator}** a crée un nouveau ticket (**{channel.name}**).",
                color=0x2ECC70,
                timestamp=interactions.Timestamp.utcnow()
            )
        em2.set_footer(text=f"Author ID : {ctx.author.id} | Ticket ID : {c.lastrowid}")
        await channel_logs.send(embeds=em2)

        conn.close()
