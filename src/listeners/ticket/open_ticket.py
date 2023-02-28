import os
import sqlite3
import interactions
from datetime import datetime
from src.listeners.ticket.components.claim import ticket_claim
from src.listeners.ticket.components.close import ticket_close_reason, ticket_close


class OpenTicket(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("open_ticket")
    async def button_open(self, ctx: interactions.ComponentContext):
        guild = await ctx.get_guild()

        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        # Partie vérification limite de ticket
        c.execute("SELECT count FROM ticket_count WHERE user_id = ?", (int(ctx.author.id),))
        count = c.fetchone()
        if c.execute("SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0] in ctx.author.roles or \
                c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] in ctx.author.roles:
            pass
        else:
            if count is not None and count[0] == 0:
                return await ctx.send("Vous avez atteint la limite de ticket", ephemeral=True)

            c.execute(
                """INSERT OR REPLACE INTO ticket_count (user_id, count) VALUES (?, COALESCE((SELECT count FROM 
                ticket_count WHERE user_id=?), 0) - 1)""",
                (int(ctx.author.id), int(ctx.author.id)))
            conn.commit()

        # Partie création ticket
        channel = await guild.create_channel(
            name=f"ticket-{ctx.user.username}", type=interactions.ChannelType.GUILD_TEXT,
            parent_id=c.execute("SELECT id FROM channels WHERE type = 'ticket_parent'").fetchone()[0],
            permission_overwrites=[
                interactions.Overwrite(id=c.execute("SELECT id FROM roles WHERE name = '@everyone'").fetchone()[0],
                                       type=0, deny=2199023255551),
                interactions.Overwrite(id=int(ctx.author.id), type=1,
                                       allow=64 | 1024 | 2048 | 32768 | 65536 | 262144 | 2147483648),
                interactions.Overwrite(id=c.execute("SELECT id FROM roles WHERE type = 'Staff'").fetchone()[0], type=0,
                                       allow=64 | 1024 | 2048 | 8192 | 32768 | 65536 | 262144 | 2147483648)
            ]
        )
        await ctx.send(f"Votre ticket a été créé {channel.mention}", ephemeral=True)
        em = interactions.Embed(
            title="Nouveau ticket",
            description="Votre ticket a été ouvert.\n**Un Staff vous répondra sous peu.** Il est inutile de ping les staffs.",
            color=0x2ECC70,
            timestamp=datetime.utcnow()
        )
        message = await channel.send(embeds=em, components=[ticket_close(), ticket_close_reason(), ticket_claim()])
        await message.pin()

        # Partie Database
        author_id = ctx.author.id

        c.execute("INSERT INTO ticket VALUES (NULL, '{}', '{}', '{}')".format(author_id, None, channel.id))
        conn.commit()

        # Partie Logs
        channel_logs = await interactions.get(self.bot,
                                              interactions.Channel,
                                              object_id=c.execute(
                                                  "SELECT id FROM logs_channels WHERE name = 'create'").fetchone()[0])

        logs_create = await interactions.get(self.bot, interactions.Channel, object_id=channel_logs.id)
        em2 = interactions.Embed(
            title="Nouveau ticket",
            description=f"**{ctx.author.username}#{ctx.author.discriminator}** a crée un nouveau ticket (**{channel.name}**).",
            color=0x2ECC70,
            timestamp=datetime.utcnow()
        )
        em2.set_footer(text=f"Author ID : {ctx.author.id} | Ticket ID : {c.lastrowid}")
        await logs_create.send(embeds=em2)

        conn.close()


def setup(bot):
    OpenTicket(bot)
