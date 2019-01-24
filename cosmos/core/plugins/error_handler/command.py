from abc import ABC

from ...functions import Cog


class CommandErrorHandler(Cog, ABC):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
