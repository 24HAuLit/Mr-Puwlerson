import interactions
from interactions.ext.voice import VoiceState


class BesoinAide(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot

    @interactions.extension_listener(name="on_voice_state_update")
    async def bda_join(self, vs: VoiceState):
        # if vs.channel_id == DATA["principal"]["bda_waiting"]:
        #     user_id = vs.user_id
        #     now = datetime.now()
        #     current_time = now.strftime("%Hh%M")
        #
        #     # Database
        #     # conn = sqlite3.connect(":memory:")
        #     # c = conn.cursor()
        #     # if self.count == 0:
        #     #     create_table = "CREATE TABLE temporary(user_id INTEGER not null )"
        #     #     c.execute(create_table)
        #     # c.execute("INSERT INTO temporary VALUES ('{}')".format(user_id))
        #
        #     guild = await interactions.get(self.bot, interactions.Guild, object_id=DATA["principal"]["guild"])
        #     channel = await guild.create_channel(
        #         name=f"🚧・{current_time}", type=interactions.ChannelType.GUILD_VOICE,
        #         parent_id=1057341701674520656,
        #         permission_overwrites=[
        #             interactions.Overwrite(id=419529681885331456, type=0, deny=2199023255551),
        #             interactions.Overwrite(id=int(vs.user_id), type=1,
        #                                    allow=1024 | 2048 | 32768 | 65536 | 262144 | 2097152 | 2147483648),
        #             interactions.Overwrite(id=1018602650566139984, type=0,
        #                                    allow=1024 | 2048 | 8192 | 32768 | 65536 | 262144 | 1048576 | 2097152 | 4194304 | 8388608 | 16777216 | 2147483648)
        #         ]
        #     )
        #     await vs.move_member(channel_id=int(channel.id), reason="None")
        pass


def setup(bot):
    BesoinAide(bot)
