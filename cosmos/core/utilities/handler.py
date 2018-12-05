from cosmos.core.utilities import handlers
from cosmos.core.utilities.utils import Utils


class Utility(Utils):

    def __init__(self, bot):
        self.bot = bot
        self.file_handler = handlers.FileHandler()
