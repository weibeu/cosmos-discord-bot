from .. import Cog


class Levels(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    @Cog.listener()
    async def on_message(self, message):
        pass
