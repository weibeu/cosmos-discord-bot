class AutoModerationActions(object):

    def __init__(self, guild_profile):
        self._profile = guild_profile

    @property
    def embed(self):
        return self._profile.plugin.bot.themes.embed.one_line.primary

    @staticmethod
    async def delete(message=None, **_):
        await message.delete()

    async def warn(self, *, member, **kwargs):
        pass

    async def mute(self, *, member, **kwargs):
        pass

    async def kick(self, *, member, **kwargs):
        pass

    async def ban(self, *, member, **kwargs):
        pass
