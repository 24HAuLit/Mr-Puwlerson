import interactions


def ticket_close():
    return interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="🔒 Fermer le ticket",
        custom_id="close_ticket",
    )


def confirm_close():
    return interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="🔒 Confirmer la fermeture",
        custom_id="confirm_close",
    )


def ticket_close_reason():
    return interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="🔒 Fermer le ticket avec raison",
        custom_id="close_reason_ticket",
    )
