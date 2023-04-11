import os
import sqlite3
import interactions
from message_config import ErrorMessage


class BannedChannels(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_command()
    @interactions.option(
        type=interactions.OptionType.CHANNEL,
        description="Salon qui sera/ ne sera pas affiché dans les logs.",
        required=True
    )
    async def banned_channels(self, ctx: interactions.CommandContext, channel: interactions.Channel):
        """Permet d'ajouter/ supprimer un salon bannis"""

        if os.path.exists(f"./Database/{ctx.guild.id}.db") is False:
            return await ctx.send(ErrorMessage.database_not_found(ctx.guild.id), ephemeral=True)

        conn = sqlite3.connect(f"./Database/{ctx.guild.id}.db")
        c = conn.cursor()

        if ctx.author.id == ctx.guild.owner_id or c.execute("SELECT id FROM roles WHERE type = 'Owner'").fetchone()[0] \
                in ctx.author.roles:

            is_hidden = c.execute(f"SELECT hidden FROM channels WHERE id = {channel.id}")
            if is_hidden.fetchone()[0] == 1:
                c.execute(f"UPDATE channels SET hidden = 0 WHERE id = {channel.id}")
                conn.commit()
                conn.close()
                return await ctx.send(f"Le salon `{channel.name}` sera désormais affiché dans les logs.", ephemeral=True)
            else:
                c.execute(f"UPDATE channels SET hidden = 1 WHERE id = {channel.id}")
                conn.commit()
                conn.close()
                return await ctx.send(f"Le salon `{channel.name}` ne sera plus affiché dans les logs.", ephemeral=True)


def setup(bot):
    BannedChannels(bot)
