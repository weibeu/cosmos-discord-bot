"""
Cosmos: A General purpose Discord bot.
Copyright (C) 2020 thec0sm0s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)

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
        self.logger.addHandler(handler)

    def set_stdout_handler(self):
        handler = logging.StreamHandler()
        self.logger.addHandler(handler)

    def set_level(self, level):
        self.logger.setLevel(level)

    def info(self, message: str):
        return self.logger.info(message)

    def debug(self, message: str):
        return self.logger.debug(message)

    def error(self, message: str):
        return self.logger.error(message)

    def warn(self, message: str):
        return self.warning(message)

    def warning(self, message: str):
        return self.logger.warning(message)

    def exception(self, message: str):
        return self.logger.exception(message)
