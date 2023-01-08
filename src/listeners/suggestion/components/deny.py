import interactions


def suggest_deny():
    return interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="Refuser",
        custom_id="refuse"
    )


def modal_deny():
    return interactions.Modal(
        title="Raison",
        custom_id="refuse_reason",
        components=[
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label="Pour quelle raison avez-vous refusé ?",
                custom_id="text_input_accept_response",
                min_length=1,
                max_length=100
            )
        ]
    )
