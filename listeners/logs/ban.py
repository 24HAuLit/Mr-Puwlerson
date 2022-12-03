import interactions
from datetime import datetime


class Ban(interactions.Extension):

    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_listener(name="on_guild_ban_add")
    async def ban(self, user: interactions.User):
        logs_ban = await interactions.get(self.bot, interactions.Channel, object_id=1025706023333408878)
        guild = await interactions.get(self.bot, interactions.Guild, object_id=int(user.guild_id))
        staff_audit = await guild.get_full_audit_logs(action_type=22)
        staff = staff_audit.audit_log_entries[0].user_id
        reason = staff_audit.audit_log_entries[0].reason

        if reason is None:
            reason = "Aucune raison spécifié"

        em = interactions.Embed(
            title="Nouveau bannissement",
            description=f"Un membre vient de se faire bannir de **{guild.name}**.",
            color=0xFF2020,
            timestamp=datetime.utcnow()
        )
        em.add_field(name="__Staff :__", value=f"<@{staff}>", inline=True)
        em.add_field(name="__Membre :__", value=user.user.mention, inline=True)
        em.add_field(name="__Raison :__", value=reason)
        em.set_footer(text=f"Staff ID : {staff} | User ID : {user.user.id}")

        await logs_ban.send(embeds=em)

    @interactions.extension_listener(name="on_guild_ban_remove")
    async def unban(self, user: interactions.User):
        logs_ban = await interactions.get(self.bot, interactions.Channel, object_id=1025706023333408878)
        guild = await interactions.get(self.bot, interactions.Guild, object_id=int(user.guild_id))
        staff_audit = await guild.get_full_audit_logs(action_type=23)
        staff = staff_audit.audit_log_entries[0].user_id

        em = interactions.Embed(
            title="Nouveau débannissement",
            description=f"Un membre vient de se faire débannir de **{guild.name}**.",
            color=0x3FFF20,
            timestamp=datetime.utcnow()
        )
        em.add_field(name="__Staff :__", value=f"<@{staff}>", inline=True)
        em.add_field(name="__Membre :__", value=user.user.mention, inline=True)
        em.set_footer(text=f"Staff ID : {staff} | User ID : {user.user.id}")

        await logs_ban.send(embeds=em)


def setup(bot):
    Ban(bot)
