import discord


def ticket_open():
    return discord.ui.Button(style=discord.ButtonStyle.primary, label="📨 Ouvrir un ticket", custom_id="open_ticket")
