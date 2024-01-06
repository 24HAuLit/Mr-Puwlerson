import os.path
import sqlite3
import interactions
from interactions.api.events import BanCreate, BanRemove


class Ban(interactions.Extension):

    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.listen(BanCreate)
    async def ban(self, user: BanCreate):
        guild = user.guild

        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        logs_ban = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'ban'").fetchone()[0])

        history = guild.audit_log_history(action_type=22)
        staff_audit = await history.flatten()
        staff_id = staff_audit[0].user_id
        reason = staff_audit[0].reason

        if reason is None:
            reason = "Aucune raison spécifié"

        em = interactions.Embed(
            title="🛑・Nouveau bannissement",
            description=f"Un membre vient de se faire bannir de **{guild.name}**.",
            color=0xFF2020,
            timestamp=interactions.Timestamp.utcnow()
        )
        em.add_field(name="__Staff :__", value=f"<@{staff_id}>", inline=True)
        em.add_field(name="__Membre :__", value=user.user.mention, inline=True)
        em.add_field(name="__Raison :__", value=reason)
        em.set_footer(text=f"Staff ID : {staff_id} | User ID : {user.user.id}")

        await logs_ban.send(embeds=em)

    @interactions.listen(BanRemove)
    async def unban(self, user: BanRemove):
        guild = user.guild

        if os.path.exists(f'./Database/{guild.id}.db') is False:
            return

        conn = sqlite3.connect(f'./Database/{guild.id}.db')
        c = conn.cursor()

        logs_unban = self.bot.get_channel(c.execute("SELECT id FROM logs_channels WHERE name = 'ban'").fetchone()[0])
        history = guild.audit_log_history(action_type=23)
        staff_audit = await history.flatten()
        staff_id = staff_audit[0].user_id

        em = interactions.Embed(
            title="🟢・Nouveau débannissement",
            description=f"Un membre vient de se faire débannir de **{guild.name}**.",
            color=0x3FFF20,
            timestamp=interactions.Timestamp.utcnow()
        )
        em.add_field(name="__Staff :__", value=f"<@{staff_id}>", inline=True)
        em.add_field(name="__Membre :__", value=user.user.mention, inline=True)
        em.set_footer(text=f"Staff ID : {staff_id} | User ID : {user.user.id}")

        await logs_unban.send(embeds=em)
