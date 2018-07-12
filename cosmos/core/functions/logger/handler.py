from cosmos.core.functions.logger.logger import Logger


class LoggerHandler(object):

    def __init__(self, bot):
        self.bot = bot
        self.logger = Logger(self.bot)

    def create(self):
        pass