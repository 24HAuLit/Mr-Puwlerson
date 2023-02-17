import sqlite3
import interactions


class BannedChannels(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_component("banned_channels")
    async def select(self, ctx: interactions.ComponentContext, choice: list[str]):
        guild = await ctx.get_guild()
        conn = sqlite3.connect(f"./Database/{guild.id}.db")
        c = conn.cursor()

        for i in range(len(choice)):
            c.execute(f"""SELECT hidden from channels WHERE id = {int(choice[i])}""")
            row = c.fetchone()
            if row is None:
                c.execute(f"""INSERT INTO channels VALUES (name ,{choice[i]}, NULL, 1)""")
                channel = await interactions.get(self.bot, interactions.Channel, object_id=int(choice[i]))
                await ctx.send(f"**{channel.name}** est désormais un channel 'banni' des logs", ephemeral=True)
            elif row[0] == 1:
                c.execute(f"""UPDATE channels SET hidden = 0 WHERE id = {choice[i]}""")
                channel = await interactions.get(self.bot, interactions.Channel, object_id=int(choice[i]))
                await ctx.send(f"**{channel.name}** n'est plus un channel 'banni' des logs", ephemeral=True)
            else:
                c.execute(f"""UPDATE channels SET hidden = 1 WHERE id = {choice[i]}""")
                channel = await interactions.get(self.bot, interactions.Channel, object_id=int(choice[i]))
                await ctx.send(f"**{channel.name}** est désormais un channel 'banni' des logs", ephemeral=True)

        conn.commit()
        conn.close()


def setup(bot):
    BannedChannels(bot)
