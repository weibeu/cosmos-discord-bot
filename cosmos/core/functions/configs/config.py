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

import os

from abc import ABC
from ...utilities import handlers


class Config(ABC):

    NAME = str()
    PATH = str()

    def __init__(self):
        self.raw = None
        self.PATH = os.path.join(self.PATH)
        self._fetch_config()

    def _fetch_config(self):
        self.raw = handlers.FileHandler.get_file_data(self.PATH)
        for config in self.raw:
            if self.raw[config] == "":
                self.raw[config] = None
            if config.endswith("_KEY") or config.endswith("_SECRET"):
                self.raw[config] = os.getenv(config) or self.raw[config]
            self.__setattr__(config, self.raw[config])
