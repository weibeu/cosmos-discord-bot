from abc import ABC

from ...functions import Cog


class BotErrorHandler(Cog, ABC):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
