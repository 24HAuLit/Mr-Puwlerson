import discord


def suggest_accept():
    return discord.ui.Button(style=discord.ButtonStyle.success, label='Accepter', custom_id='accept')


class AcceptReason(discord.ui.Modal, title='Raison'):
    reason = discord.ui.TextInput(label='Raison', placeholder='Pour quelle raison avez-vous accepté ?', style=discord.TextStyle.paragraph, max_length=100, custom_id='acc_short_response')

    def __init__(self, callback):
        super().__init__(custom_id='accept_reason')
        self.callback = callback

    async def on_submit(self, interaction: discord.Interaction):
        await self.callback(interaction)


def modal_accept(callback):
    return AcceptReason(callback)
