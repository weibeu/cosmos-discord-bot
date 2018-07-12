import logging
import os


class Logger(object):

    def __init__(self, bot):
        self.bot = bot
        self.default_format = self.bot.configs.logger.format
        self.default_date_format = self.bot.configs.logger.date_format
        self.style = self.bot.configs.logger.style
        self.name = self.bot.configs.logger.name
        self.path = self.bot.configs.logger.path
        self.file_name = self.bot.configs.logger.file_name
        self.level = logging.DEBUG
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(self.level)
        self.handler = None

    def set_file_handler(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self.handler = logging.FileHandler(filename=os.path.join(self.path, self.file_name), encoding="utf-8", mode="w")
        logger_format = logging.Formatter(fmt=self.default_format, datefmt=self.default_date_format, style=self.style)
        self.handler.setFormatter(logger_format)
        self._logger.addHandler(self.handler)

    def set_level(self, level):
        self._logger.setLevel(level)
