from ... import Cog


class LoggerEvents(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    @Cog.listener()
    async def on_message_delete(self, message):
        pass

    @Cog.listener()
    async def on_bulk_message_delete(self, messages):
        pass

    @Cog.listener()
    async def on_message_edit(self, before, after):
        pass

    @Cog.listener()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        pass

    @Cog.listener()
    async def on_member_join(self, member):
        pass

    @Cog.listener()
    async def on_member_remove(self, member):
        pass

    @Cog.listener()
    async def on_member_ban(self, guild, user):
        pass

    @Cog.listener()
    async def on_member_unban(self, guild, user):
        pass

    @Cog.listener()
    async def on_member_moderation(self, member, action):
        pass
