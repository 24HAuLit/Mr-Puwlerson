import os
import sqlite3
import interactions


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

    @interactions.extension_listener(name="on_channel_create")
    async def new_channel(self, channel: interactions.Channel):
        if channel.guild_id is None:
            return

        guild = await interactions.get(self.bot, interactions.Guild, object_id=channel.guild_id)
        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if channel.parent_id == c.execute("SELECT id FROM channels WHERE type = 'ticket_parent'").fetchone()[0]:
            return

        c.execute("INSERT INTO channels VALUES ('{}', '{}', NULL, '{}')".format(channel.name, channel.id, 0))

        conn.commit()

        logs = await interactions.get(self.bot, interactions.Channel, object_id=c.execute("SELECT id FROM logs_channels WHERE name = 'create-channel'").fetchone()[0])
        type = self.type[channel.type]

        em = interactions.Embed(
            title="📝・Nouveau salon",
            description=f"Un nouveau salon vient d'être créé sur **{guild.name}** ({guild.id})",
            color=0x4CFF4C
        )
        em.add_field(name="**Nom : **", value=channel.name, inline=True)
        em.add_field(name="**Type : **", value=type, inline=True)
        em.add_field(name="**ID : **", value=channel.id, inline=False)

        await logs.send(embeds=em)

    @interactions.extension_listener(name="on_channel_delete")
    async def delete_channel(self, channel: interactions.Channel):
        if channel.guild_id is None:
            return

        guild = await interactions.get(self.bot, interactions.Guild, object_id=channel.guild_id)
        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        if channel.parent_id == c.execute("SELECT id FROM channels WHERE type = 'ticket_parent'").fetchone()[0]:
            return

        c.execute(f"DELETE FROM channels WHERE id = {channel.id}")
        conn.commit()

        logs = await interactions.get(self.bot, interactions.Channel, object_id=c.execute("SELECT id FROM logs_channels WHERE name = 'delete-channel'").fetchone()[0])
        type = self.type[channel.type]

        em = interactions.Embed(
            title="🗑️・Suppression de salon",
            description=f"Un salon vient d'être supprimé sur **{guild.name}** ({guild.id})",
            color=0xFF5A5A
        )
        em.add_field(name="**Nom : **", value=channel.name, inline=True)
        em.add_field(name="**Type : **", value=type, inline=True)
        em.add_field(name="**ID : **", value=channel.id, inline=False)

        await logs.send(embeds=em)


def setup(bot):
    OnChannel(bot)
