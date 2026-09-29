import discord


def confirm():
    return discord.ui.Button(style=discord.ButtonStyle.success, label="📩 Oui, envoyer", custom_id="send")


def cancel():
    return discord.ui.Button(style=discord.ButtonStyle.danger, label="Non, ne pas envoyer", custom_id="cancel")
