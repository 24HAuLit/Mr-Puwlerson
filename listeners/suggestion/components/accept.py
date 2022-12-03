import interactions


def suggest_accept():
    return interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="Accepter",
        custom_id="accept"
    )


def modal_accept():
    return interactions.Modal(
        title="Raison",
        custom_id="accept_reason",
        components=[
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label="Pour quelle raison avez-vous accepté ?",
                custom_id="text_input_accept_response",
                min_length=1,
                max_length=15
            )
        ]
    )
