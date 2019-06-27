class AutoModerationActions(object):

    def __init__(self, guild_profile):
        self._profile = guild_profile

    async def delete(self, message=None, **kwargs):
        pass

    async def warn(self, *, member, **kwargs):
        pass

    async def mute(self, *, member, **kwargs):
        pass

    async def kick(self, *, member, **kwargs):
        pass

    async def ban(self, *, member, **kwargs):
        pass
