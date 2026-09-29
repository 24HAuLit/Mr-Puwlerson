import sqlite3

import discord
from discord.ext import commands

from mr_puwlerson.listeners import database_path


class OnNewGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        if database_path(guild.id).exists():
            return
        print(f'New guild: {guild.name}')
        with sqlite3.connect(database_path(guild.id)) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS blacklist(blacklist_id integer primary key autoincrement, user_id integer, reason text);
                CREATE TABLE IF NOT EXISTS channels(name text, id integer, type text default NULL, hidden integer default 0);
                CREATE TABLE IF NOT EXISTS logs_channels(name text, id integer);
                CREATE TABLE IF NOT EXISTS plugins(name text, status text default 'false');
                CREATE TABLE IF NOT EXISTS roles(name text, id integer, type text default NULL);
                CREATE TABLE IF NOT EXISTS ticket(ticket_id integer primary key autoincrement, author_id integer, staff_id integer, channel_id integer);
                CREATE TABLE IF NOT EXISTS ticket_count(user_id integer, count integer default 0);
            ''')


async def setup(bot):
    await bot.add_cog(OnNewGuild(bot))
