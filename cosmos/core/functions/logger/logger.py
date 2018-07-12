import logging


class Logger(object):

    def __init__(self, bot):
        self.bot = bot
        self.default_format = self.bot.configs.logger.format
        self.default_date_format = self.bot.configs.logger.date_format
        self.name = self.bot.configs.logger.name
