import interactions


def ticket_embed():
    em = interactions.Embed(
        title="Création de ticket",
        description="Ici vous pourrez créer un ticket pour avoir de l'aide. **Il est inutile de mentionner des "
                    "Staffs** si vous n'avez pas eu de réponses dans **un délai de 24 heures**. ",
        color=0x2F3136
    )
    return em

