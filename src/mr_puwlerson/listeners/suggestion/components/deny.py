import discord


def suggest_deny():
    return discord.ui.Button(style=discord.ButtonStyle.danger, label='Refuser', custom_id='refuse')


class DenyReason(discord.ui.Modal, title='Raison'):
    reason = discord.ui.TextInput(label='Raison', placeholder='Pour quelle raison avez-vous refusé ?', style=discord.TextStyle.paragraph, max_length=100, custom_id='deny_short_response')

    def __init__(self, callback):
        super().__init__(custom_id='refuse_reason')
        self.callback = callback

    async def on_submit(self, interaction: discord.Interaction):
        await self.callback(interaction)


def modal_deny(callback):
    return DenyReason(callback)
