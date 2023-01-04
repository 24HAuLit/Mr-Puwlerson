from interactions import Button, ButtonStyle


def confirm():
    return Button(
        style=ButtonStyle.SUCCESS,
        label="📩 Oui, envoyer",
        custom_id="send"
    )


def cancel():
    return Button(
        style=ButtonStyle.DANGER,
        label="Non, ne pas envoyer",
        custom_id="cancel"
    )
