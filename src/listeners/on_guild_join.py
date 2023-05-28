import interactions
import os
import sqlite3


class OnNewGuild(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_listener(name="on_guild_join")
    async def new_guild(self, guild: interactions.Guild):
        if os.path.exists(f'./Database/{guild.id}.db') is True:
            return
        else:
            conn = sqlite3.connect(f'./Database/{guild.id}.db')
            c = conn.cursor()

            c.execute("""CREATE TABLE blacklist (
                blacklist_id integer primary key autoincrement,
                user_id integer,
                reason text                
            )""")

            c.execute("""CREATE TABLE channels (
                name text,
                id integer,
                type text default NULL,
                hidden integer default 0
            )""")

            c.execute("""CREATE TABLE locale (
                locale text default 'en'
            )""")

            c.execute("""CREATE TABLE logs_channels (
                name text,
                id integer
            )""")

            c.execute("""CREATE TABLE plugins (
                name text,
                status text default 'false'
            )""")

            c.execute("""CREATE TABLE roles (
                name text,
                id integer,
                type text default NULL
            )""")

            c.execute("""CREATE TABLE tickets (
                ticket_id integer primary key autoincrement,
                author_id integer,
                staff_id integer,
                channel_id integer
            )""")

            c.execute("""CREATE TABLE ticket_count (
                user_id integer,
                count integer default 0
            )""")

            conn.commit()


def setup(bot):
    OnNewGuild(bot)
