import interactions


def ticket_claim():
    return interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="🙋‍♂️ Prendre le ticket",
        custom_id="claim_ticket",
    )
