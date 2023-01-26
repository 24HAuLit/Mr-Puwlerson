import sqlite3

import interactions
from const import DATA


class Test(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    async def embed(self, ctx):
        pass
        # user = await interactions.get(self.bot, interactions.User, object_id=464404008396914688)
        # channel = await interactions.get(self.bot, interactions.Channel, object_id=DATA["main"]["suggestion"])
        # em = interactions.Embed(title="Création de suggestion",
        #                         description="Pour proposer une suggestion, il suffit d'écrire la commande `/suggest ("
        #                                     "Suggestion)` dans n'importe quel salon.\nVotre suggestion sera "
        #                                     "directement écrite dans le salon "
        #                                     "<#1011704888679477369>. Si cette dernière est accepté, vous le verrez "
        #                                     "dans le salon <#1011705768002727987>.", color=0x2F3136)
        # em.set_footer(icon_url=f"{user.avatar_url}", text=f"Mr. Puwlerson, esclave à temps plein.")
        # await channel.send(embeds=em)


def setup(bot):
    Test(bot)
