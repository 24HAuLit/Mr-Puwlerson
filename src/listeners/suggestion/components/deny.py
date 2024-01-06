import interactions


def suggest_deny():
    return interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="Refuser",
        custom_id="refuse"
    )


def modal_deny():
    return interactions.Modal(
        interactions.ParagraphText(
            label="Raison",
            placeholder="Pour quelle raison avez-vous refusé ?",
            custom_id="deny_short_response",
            max_length=100
        ),
        title="Raison",
        custom_id="refuse_reason"
    )
