from ...functions import Cog


class BotErrorHandler(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
