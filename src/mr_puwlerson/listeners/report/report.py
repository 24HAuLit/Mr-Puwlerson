import sqlite3
from datetime import UTC, datetime

import discord
from discord.ext import commands

from mr_puwlerson.listeners import view
from mr_puwlerson.listeners.report.components.components import cancel, confirm


class ReportListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is not None:
            return
        with sqlite3.connect('./Database/419529681885331456.db') as conn:
            blocked = conn.execute('SELECT 1 FROM blacklist WHERE user_id = ?', (message.author.id,)).fetchone()
            log_id = conn.execute("SELECT id FROM logs_channels WHERE name = 'report'").fetchone()[0]
        if blocked:
            await message.channel.send('Vous êtes blacklisté des reports.')
            return
        prompt = await message.channel.send('Êtes-vous sur de vouloir faire ce report ? **Tout abus se verra sanctionné d\'un blacklist report!**', view=view(confirm(), cancel()))

        def check(interaction):
            return (interaction.type == discord.InteractionType.component and interaction.message.id == prompt.id
                    and interaction.user.id == message.author.id and interaction.data.get('custom_id') in ('send', 'cancel'))

        try:
            interaction = await self.bot.wait_for('interaction', check=check, timeout=15)
        except TimeoutError:
            await prompt.edit(view=None)
            return
        await interaction.response.edit_message(view=None)
        if interaction.data['custom_id'] == 'cancel':
            await interaction.followup.send('Vous avez annulé votre report.')
            return
        embed = discord.Embed(title='🎯・Nouveau report', description=message.content, timestamp=datetime.now(UTC))
        embed.set_footer(icon_url=message.author.display_avatar.url, text=f'Report envoyé par {message.author} | ID : {message.author.id}')
        await interaction.followup.send('Votre report a bien été transmis aux staff, ces derniers vont s\'en occuper dans les plus bref délais.')
        await self.bot.get_channel(log_id).send(embed=embed)


async def setup(bot):
    await bot.add_cog(ReportListener(bot))
