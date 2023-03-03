import asyncio
import sqlite3
import interactions
from datetime import datetime
from src.listeners.report.components.components import confirm, cancel
from message_config import ErrorMessage


class Report(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_listener()
    async def on_message_create(self, message: interactions.Message):
        if message.author.bot:
            return

        channel = await message.get_channel()
        content = message.content

        conn = sqlite3.connect('./Database/419529681885331456.db')
        c = conn.cursor()
        c.execute(f'SELECT * from blacklist WHERE user_id = {int(message.author.id)}')
        row = c.fetchone()

        if channel.type == interactions.ChannelType.DM:
            if row is not None:
                await channel.send(ErrorMessage.BlacklistError())
            else:
                confirm_message = await channel.send(
                    "Êtes-vous sur de vouloir faire ce report ? **Tout abus se verra sanctionné d'un blacklist "
                    "report!**",
                    components=[confirm(), cancel()])

                @interactions.extension_component("send")
                async def report_confirm(ctx):
                    return int(ctx.user.id)

                try:
                    button_ctx: interactions.ComponentContext = await self.bot.wait_for_component(
                        components=confirm(), check=report_confirm, timeout=15
                    )
                    report_channel = await interactions.get(self.bot, interactions.Channel, object_id=c.execute("SELECT id FROM logs_channels WHERE name = 'report'").fetchone()[0])
                    em_report = interactions.Embed(
                        title="🎯・Nouveau report",
                        description=content,
                        timestamp=datetime.utcnow()
                    )
                    em_report.set_footer(
                        icon_url=message.author.avatar_url,
                        text=f"Report envoyé par {message.author}#{message.author.discriminator} | ID : {message.author.id}"
                    )
                    await confirm_message.edit(components=[])
                    await button_ctx.send(
                        "Votre report a bien été transmis aux staff, ces derniers vont s'en occuper dans les plus bref délais.")
                    await report_channel.send(embeds=em_report)
                except asyncio.TimeoutError:
                    return await confirm_message.edit(components=[])

        conn.close()
        return


def setup(bot):
    Report(bot)
