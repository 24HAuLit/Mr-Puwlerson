import discord


def ticket_close():
    return discord.ui.Button(style=discord.ButtonStyle.danger, label="🔒 Fermer le ticket", custom_id="close_ticket")


def confirm_close():
    return discord.ui.Button(style=discord.ButtonStyle.danger, label="🔒 Confirmer la fermeture", custom_id="confirm_close")


def confirm_close_cmd():
    return discord.ui.Button(style=discord.ButtonStyle.danger, label="🔒 Confirmer la fermeture", custom_id="confirm_close_cmd")


def ticket_close_reason():
    return discord.ui.Button(style=discord.ButtonStyle.danger, label="🔒 Fermer le ticket avec raison", custom_id="close_reason_ticket")
