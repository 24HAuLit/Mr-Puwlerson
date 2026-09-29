import random
import sqlite3
import string

import discord
from discord.ext import commands

from mr_puwlerson.listeners import database_path, view


class OnUserJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        if not database_path(guild.id).exists():
            return
        with sqlite3.connect(database_path(guild.id)) as conn:
            config = conn.execute('SELECT auto_role, default_role FROM config').fetchone()
            if config[0] == 1:
                role = guild.get_role(config[1])
                if role is not None:
                    await member.add_roles(role)
            elif config[0] == 2 and not member.bot:
                codes = [''.join(random.choices(string.ascii_letters + string.digits, k=5)) for _ in range(3)]
                correct = random.choice(codes)
                buttons = [discord.ui.Button(style=discord.ButtonStyle.secondary, label=code, custom_id=code) for code in codes]
                with sqlite3.connect('./Database/temp_join.db') as temporary:
                    temporary.execute("INSERT INTO 'join' VALUES (?, ?)", (member.id, guild.id))
                conn.execute('INSERT INTO antiraid VALUES (?, ?)', (member.id, correct))
                embed = discord.Embed(title='🚧・Verification', description=f'Salut à toi {member.mention}.\n\nPour pouvoir accéder au serveur **{guild.name}**, il vous faudra appuyer sur le boutton contenant le code suivant :\n\n`{correct}`', color=0xFFD500)
                await member.send(embed=embed, view=view(*buttons))

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if (interaction.type != discord.InteractionType.component or interaction.guild_id is not None
                or interaction.data is None or interaction.message is None):
            return
        with sqlite3.connect('./Database/temp_join.db') as temporary:
            row = temporary.execute("SELECT guild_id FROM 'join' WHERE user_id = ?", (interaction.user.id,)).fetchone()
            if row is None:
                return
            guild = self.bot.get_guild(row[0])
            if guild is None:
                return
            with sqlite3.connect(database_path(guild.id)) as conn:
                code = conn.execute('SELECT code FROM antiraid WHERE member = ?', (interaction.user.id,)).fetchone()
                buttons = [button.custom_id for row in interaction.message.components if isinstance(row, discord.ActionRow) for button in row.children if isinstance(button, discord.Button)]
                custom_id = interaction.data.get('custom_id')
                if code is None or custom_id not in buttons:
                    return
                if custom_id != code[0]:
                    return await interaction.response.send_message("Vous n'avez pas appuyé sur le bon boutton !")
                temporary.execute("DELETE FROM 'join' WHERE user_id = ?", (interaction.user.id,))
                conn.execute('DELETE FROM antiraid WHERE member = ?', (interaction.user.id,))
                role_id = conn.execute('SELECT default_role FROM config').fetchone()[0]
        await interaction.response.edit_message(view=None)
        await interaction.followup.send('Vous avez appuyé sur le bon boutton. Vous êtes donc vérifié !')
        member = guild.get_member(interaction.user.id) or await guild.fetch_member(interaction.user.id)
        role = guild.get_role(role_id)
        if role is not None:
            await member.add_roles(role, reason='Verification passed')


async def setup(bot):
    await bot.add_cog(OnUserJoin(bot))
