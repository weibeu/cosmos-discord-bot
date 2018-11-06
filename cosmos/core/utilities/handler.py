from cosmos.core.utilities import handlers


class Utility(object):

    def __init__(self, bot):
        self.bot = bot
        self.file_handler = handlers.FileHandler(self.bot)
