import os
import sqlite3
import interactions
from interactions.api.events import ChannelCreate, ChannelDelete, ChannelUpdate


class OnChannel(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.type = {
            0: "Text",
            1: "DM",
            2: "Voice",
            3: "Group DM",
            4: "Category",
            5: "Announcement",
            6: "Store",
            7: "Announcement Thread",
            8: "Public Thread",
            9: "Private Thread",
            10: "Stage Voice",
            11: "Directory",
            12: "Forum",
        }
        self.none = None

    @interactions.listen(ChannelCreate)
    async def new_channel(self, base_channel: ChannelCreate):
        if base_channel.channel.guild.id is None:
            return

        guild = self.bot.get_guild(base_channel.channel.guild.id)
        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if base_channel.channel.parent_id == c.execute("SELECT ticket_parent FROM config").fetchone()[0]:
            return conn.close()

        c.execute("INSERT INTO channels VALUES ('{}', '{}', NULL, '{}')".format(base_channel.channel.name, base_channel.channel.id, 0))

        conn.commit()

        logs = self.bot.get_channel(
            c.execute("SELECT id FROM logs_channels WHERE name = 'create-channel'").fetchone()[0])
        types = self.type[base_channel.channel.type]

        conn.close()

        em = interactions.Embed(
            title="📝・Nouveau salon",
            description=f"Un nouveau salon vient d'être créé sur **{guild.name}** ({guild.id})",
            color=0x4CFF4C
        )
        em.add_field(name="**Nom : **", value=base_channel.channel.name, inline=True)
        em.add_field(name="**Type : **", value=types, inline=True)
        em.add_field(name="**ID : **", value=base_channel.channel.id, inline=False)

        await logs.send(embeds=em)

    @interactions.listen(ChannelDelete)
    async def delete_channel(self, base_channel: interactions.events.ChannelDelete):
        if base_channel.channel is None:
            return

        if base_channel.channel.guild.id is None:
            return

        guild = self.bot.get_guild(base_channel.channel.guild.id)
        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if base_channel.channel.parent_id == c.execute("SELECT ticket_parent FROM config").fetchone()[0]:
            return conn.close()

        c.execute(f"DELETE FROM channels WHERE id = {base_channel.channel.id}")
        conn.commit()

        logs = self.bot.get_channel(
            c.execute("SELECT id FROM logs_channels WHERE name = 'delete-channel'").fetchone()[0])
        types = self.type[base_channel.channel.type]

        conn.close()

        em = interactions.Embed(
            title="🗑️・Suppression de salon",
            description=f"Un salon vient d'être supprimé sur **{guild.name}** ({guild.id})",
            color=0xFF5A5A
        )
        em.add_field(name="**Nom : **", value=base_channel.channel.name, inline=True)
        em.add_field(name="**Type : **", value=types, inline=True)
        em.add_field(name="**ID : **", value=base_channel.channel.id, inline=False)

        await logs.send(embeds=em)
