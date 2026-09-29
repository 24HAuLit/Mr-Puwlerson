import discord


def ticket_claim():
    return discord.ui.Button(style=discord.ButtonStyle.success, label="🙋‍♂️ Prendre le ticket", custom_id="claim_ticket")
