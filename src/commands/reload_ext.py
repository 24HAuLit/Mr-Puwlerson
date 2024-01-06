import interactions
from src.utils.message_config import ErrorMessage


class ReloadExtension(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.slash_command()
    @interactions.slash_option(
        name="extension",
        description="Extension to reload",
        opt_type=interactions.OptionType.STRING,
        required=True
    )
    async def reload_ext(self, ctx: interactions.SlashContext, extension: str):
        """Allows you to reload an extension."""
        if ctx.author.id in self.bot.owners:
            try:
                self.bot.reload_extension(extension)
                await ctx.send(f"Extension **{extension}** has been reloaded.", ephemeral=True)
            except Exception as e:
                await ctx.send(f"Cannot reload the extension **{extension}** : {e}", ephemeral=True)
        else:
            await ctx.send(ErrorMessage.MissingPermissions(ctx.guild.id), ephemeral=True)
