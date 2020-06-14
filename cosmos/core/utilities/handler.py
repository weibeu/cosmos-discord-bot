from . import handlers

from .utils import Utils
from .api import ImgurClient


class Utility(Utils):

    def __init__(self, bot):
        self.bot = bot
        self.file_handler = handlers.FileHandler()
        self.imgur = ImgurClient(self.bot.configs.imgur.client_id)
