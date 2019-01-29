import logging
import os


class Logger(object):

    def __init__(self, bot):
        self.bot = bot
        self.default_format = self.bot.configs.logger.format
        self.default_date_format = self.bot.configs.logger.date_format
        self.style = self.bot.configs.logger.style
        self.name = self.bot.configs.logger.name
        self.path = self.bot.configs.logger.path.format(**self.bot.time.now().__dict__)
        self.file_name = self.bot.configs.logger.file_name.format(**self.bot.time.now().__dict__)
        self.level = getattr(logging, self.bot.configs.logger.level)
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(self.level)

    def set_file_handler(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        if self.file_name not in os.listdir(self.path):
            print(f"Creating log file '{os.path.join(self.path, self.file_name)}'.", end=" ")
        else:
            print(f"Using '{os.path.join(self.path, self.file_name)}' as log file.", end=" ")
        handler = logging.FileHandler(filename=os.path.join(self.path, self.file_name), encoding="utf-8")
        print("Done.")
        logger_format = logging.Formatter(fmt=self.default_format, datefmt=self.default_date_format, style=self.style)
        handler.setFormatter(logger_format)
        self._logger.addHandler(handler)

    def set_stdout_handler(self):
        handler = logging.StreamHandler()
        self._logger.addHandler(handler)

    def set_level(self, level):
        self._logger.setLevel(level)

    def info(self, message: str):
        return self._logger.info(message)

    def debug(self, message: str):
        return self._logger.debug(message)

    def error(self, message: str):
        return self._logger.error(message)

    def warn(self, message: str):
        return self.warning(message)

    def warning(self, message: str):
        return self._logger.warning(message)

    def exception(self, message: str):
        return self._logger.exception(message)
