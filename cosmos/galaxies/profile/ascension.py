from .. import Cog


class Levels(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.cache

    def __is_ignored(self, message):
        if message.author.id == self.bot.user.id:
            return True
        if message.author.bot:
            return True
        if not message.guild:
            return True

    @Cog.listener()
    async def on_message(self, message):
        if self.__is_ignored(message):
            return

        await self.cache.give_assets(message)
