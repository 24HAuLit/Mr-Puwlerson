import sqlite3
import interactions
from datetime import datetime
from src.listeners.ticket.components.claim import ticket_claim
from src.listeners.ticket.components.close import ticket_close_reason, ticket_close


class OpenTicket(interactions.Extension):

    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("open_ticket")
    async def button_open(self, ctx):
        conn = sqlite3.connect('./Database/puwlerson.db')
        c = conn.cursor()

        # Partie création ticket
        guild = await interactions.get(self.bot, interactions.Guild, object_id=419529681885331456)
        channel = await guild.create_channel(
            name=f"ticket-{ctx.user.username}", type=interactions.ChannelType.GUILD_TEXT,
            parent_id=1027647411495129109,
            permission_overwrites=[
                interactions.Overwrite(id=419529681885331456, type=0, deny=2199023255551),
                interactions.Overwrite(id=int(ctx.author.id), type=1,
                                       allow=64 | 1024 | 2048 | 32768 | 65536 | 262144 | 2147483648),
                interactions.Overwrite(id=1018602650566139984, type=0,
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

        c.execute("INSERT INTO ticket VALUES (NULL, '{}', '{}', '{}', '{}')".format(author_id, None, channel.id, 0))
        conn.commit()
        conn.close()

        # Partie Logs
        logs_create = await interactions.get(self.bot, interactions.Channel, object_id=1030764531720392734)
        em2 = interactions.Embed(
            title="Nouveau ticket",
            description=f"**{ctx.author.username}#{ctx.author.discriminator}** a crée un nouveau ticket (**{channel.name}**).",
            color=0x2ECC70,
            timestamp=datetime.utcnow()
        )
        em2.set_footer(text=f"Author ID : {ctx.author.id} | Ticket ID : {c.lastrowid}")
        await logs_create.send(embeds=em2)


def setup(bot):
    OpenTicket(bot)
