import sqlite3
import interactions


class TicketCategory(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("ticket_category")
    async def ticket_category(self, ctx: interactions.ComponentContext, choice: list[int]):
        guild = await ctx.get_guild()
        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        c.execute(f"""SELECT * FROM channels WHERE type = 'ticket_parent'""")
        row = c.fetchone()

        if row is None:
            c.execute(f"""UPDATE channels SET type = 'ticket_parent' WHERE id = {choice[0]}""")
            channel = await interactions.get(self.bot, interactions.Channel, object_id=choice[0])
            await ctx.send(f"**{channel.name}** est désormais la catégorie de tickets", ephemeral=True)
        elif row[1] == int(choice[0]):
            channel = await interactions.get(self.bot, interactions.Channel, object_id=choice[0])
            await ctx.send(f"**{channel.name}** est déjà la catégorie pour les tickets", ephemeral=True)
        else:
            c.execute(f"""UPDATE channels SET type = NULL WHERE id = {row[1]}""")
            c.execute(f"""UPDATE channels SET type = 'ticket_parent' WHERE id = {choice[0]}""")
            channel = await interactions.get(self.bot, interactions.Channel, object_id=choice[0])
            await ctx.send(f"**{row[0]}** n'est plus la catégorie pour les tickets, elle a été remplacée par **{channel.name}**", ephemeral=True)

        conn.commit()
        conn.close()


def setup(bot):
    TicketCategory(bot)



