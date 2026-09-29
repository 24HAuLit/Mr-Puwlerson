import sqlite3
from datetime import datetime, timezone

import discord
from discord.ext import commands

from mr_puwlerson.listeners import database_path, has_role, view
from mr_puwlerson.listeners.ticket.components.claim import ticket_claim
from mr_puwlerson.listeners.ticket.components.close import ticket_close, ticket_close_reason


class OpenTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component or interaction.data is None or interaction.data.get('custom_id') != 'open_ticket':
            return
        guild, user = interaction.guild, interaction.user
        if guild is None or not isinstance(user, discord.Member):
            return
        if not database_path(guild.id).exists():
            return await interaction.response.send_message('Base de données introuvable.', ephemeral=True)
        with sqlite3.connect(database_path(guild.id)) as conn:
            count = conn.execute('SELECT count FROM ticket_count WHERE user_id = ?', (user.id,)).fetchone()
            config = conn.execute('SELECT ticket_limit, ticket_parent, staff_role FROM config').fetchone()
            category = guild.get_channel(config[1])
            staff_role = guild.get_role(config[2])
            if not isinstance(category, discord.CategoryChannel) or staff_role is None:
                return await interaction.response.send_message('Configuration des tickets incomplète.', ephemeral=True)
            if not has_role(user, 'staff_role'):
                if count is not None and count[0] >= config[0]:
                    return await interaction.response.send_message('Limite de tickets atteinte.', ephemeral=True)
                if count is None:
                    conn.execute('INSERT INTO ticket_count (user_id, count) VALUES (?, 1)', (user.id,))
                else:
                    conn.execute('UPDATE ticket_count SET count = count + 1 WHERE user_id = ?', (user.id,))
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
                staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True),
            }
            try:
                channel = await guild.create_text_channel(f'ticket-{user.name}', category=category, overwrites=overwrites)
            except Exception:
                conn.rollback()
                raise
            cursor = conn.execute('INSERT INTO ticket VALUES (NULL, ?, NULL, ?)', (user.id, channel.id))
            ticket_id = cursor.lastrowid
            log_id = conn.execute("SELECT id FROM logs_channels WHERE name = 'create'").fetchone()[0]

        await interaction.response.send_message(f'Votre ticket a été créé {channel.mention}', ephemeral=True)
        embed = discord.Embed(title='Nouveau ticket', description='Votre ticket a été ouvert.\n**Un Staff vous répondra sous peu.** Il est inutile de ping les staffs.', color=0x2ECC70, timestamp=datetime.now(timezone.utc))
        embed.set_footer(text=f'Author ID : {user.id} | Ticket ID : {ticket_id}')
        message = await channel.send(embed=embed, view=view(ticket_close(), ticket_close_reason(), ticket_claim()))
        await message.pin()
        logs = self.bot.get_channel(log_id)
        log = discord.Embed(title='Nouveau ticket', description=f'**{user}** a crée un nouveau ticket (**{channel.name}**).', color=0x2ECC70, timestamp=datetime.now(timezone.utc))
        log.set_footer(text=f'Author ID : {user.id} | Ticket ID : {ticket_id}')
        await logs.send(embed=log)


async def setup(bot):
    await bot.add_cog(OpenTicket(bot))
