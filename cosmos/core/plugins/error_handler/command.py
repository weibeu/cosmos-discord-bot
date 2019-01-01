from abc import ABC

from ...functions.plugins.models import Cog


class CommandErrorHandler(Cog, ABC):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.bot = self.plugin.bot
