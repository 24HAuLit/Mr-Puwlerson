import sqlite3
import interactions
from interactions import LocalizedDesc, LocalizedName
from src.utils.checks import database_exists, is_owner


class BannedChannels(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.slash_command(
        description=LocalizedDesc(english_us="Allows you to add/ delete a 'banned channel'", french="Permet d'ajouter/ supprimer un salon bannis")
    )
    @interactions.slash_option(
        name=LocalizedName(english_us="channel", french="salon"),
        opt_type=interactions.OptionType.CHANNEL,
        description=LocalizedDesc(english_us="Channel that will (not) have logs.", french="Salon qui aura/ n'aura pas de logs."),
        required=True
    )
    async def banned_channels(self, ctx: interactions.SlashContext, channel: interactions.GuildChannel):
        if await database_exists(ctx) is not True:
            return

        if await is_owner(ctx) is not True:
            return

        conn = sqlite3.connect(f"./Database/{ctx.guild.id}.db")
        c = conn.cursor()

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
