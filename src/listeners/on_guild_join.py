import interactions
import os
import sqlite3
from interactions.api.events import GuildJoin


class OnNewGuild(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.listen(GuildJoin)
    async def new_guild(self, guild: GuildJoin):
        if os.path.exists(f'./Database/{guild.guild.id}'):
            return
        else:
            print(f"New guild: {guild.guild.name}")
            conn = sqlite3.connect(f'./Database/{guild.guild.id}.db')
            c = conn.cursor()

            c.execute("""CREATE TABLE IF NOT EXISTS blacklist(
                blacklist_id integer primary key autoincrement,
                user_id integer,
                reason text                
            )""")

            c.execute("""CREATE TABLE IF NOT EXISTS channels (
                name text,
                id integer,
                type text default NULL,
                hidden integer default 0
            )""")

            c.execute("""CREATE TABLE IF NOT EXISTS logs_channels (
                name text,
                id integer
            )""")

            c.execute("""CREATE TABLE IF NOT EXISTS plugins (
                name text,
                status text default 'false'
            )""")

            c.execute("""CREATE TABLE IF NOT EXISTS roles (
                name text,
                id integer,
                type text default NULL
            )""")

            c.execute("""CREATE TABLE IF NOT EXISTS ticket (
                ticket_id integer primary key autoincrement,
                author_id integer,
                staff_id integer,
                channel_id integer
            )""")

            c.execute("""CREATE TABLE IF NOT EXISTS ticket_count (
                user_id integer,
                count integer default 0
            )""")

            conn.commit()
            conn.close()
