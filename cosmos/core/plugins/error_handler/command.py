from ...functions import Cog


class CommandErrorHandler(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
