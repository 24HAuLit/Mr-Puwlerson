import asyncio
from datetime import datetime
import interactions
from listeners.report.components.components import confirm, cancel


class Report(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_listener()
    async def on_message_create(self, message: interactions.Message):
        if message.author.bot:
            return

        channel = await message.get_channel()
        content = message.content

        if channel.type == interactions.ChannelType.DM:
            confirm_message = await channel.send(
                "Êtes-vous sur de vouloir faire ce report ? **Tout abus se vera sanctionné d'un blacklist report!**",
                components=[confirm(), cancel()])

            @interactions.extension_component("send")
            async def report_confirm(ctx):
                return int(ctx.user.id)

            try:
                button_ctx: interactions.ComponentContext = await self.bot.wait_for_component(
                    components=confirm(), check=report_confirm, timeout=15
                )
                report_channel = await interactions.get(self.bot, interactions.Channel, object_id=1060273879018381405)
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
                await button_ctx.send("Votre report a bien été transmis aux staff, ces derniers vont s'en occuper dans les plus bref délais.")
                await report_channel.send(embeds=em_report)
            except asyncio.TimeoutError:
                return await confirm_message.edit(components=[])

        return


def setup(bot):
    Report(bot)
