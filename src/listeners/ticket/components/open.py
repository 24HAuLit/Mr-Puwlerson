import interactions


def ticket_open():
    return interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="📨 Ouvrir un ticket",
        custom_id="open_ticket",
    )
