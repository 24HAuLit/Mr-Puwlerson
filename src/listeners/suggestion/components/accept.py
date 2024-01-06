import interactions


def suggest_accept():
    return interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="Accepter",
        custom_id="accept"
    )


def modal_accept():
    return interactions.Modal(
        interactions.ParagraphText(
            label="Raison",
            placeholder="Pour quelle raison avez-vous accepté ?",
            custom_id="acc_short_response",
            max_length=100
        ),
        title="Raison",
        custom_id="accept_reason",
    )
