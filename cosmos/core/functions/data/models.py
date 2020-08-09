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

from .data import Data


class PluginData(Data):

    DATA_DIR = "data/"

    def __init__(self, bot, plugin):
        self.bot = bot
        self.plugin = plugin
        self.data_dir = None    # Raw data.
        self.fetch_plugin_dir()
        super().__init__(self.bot, self.data_dir)   # Vomit plugin data directory to Data superclass.

    def fetch_plugin_dir(self):
        self.data_dir = os.path.join(self.plugin.dir_path, self.DATA_DIR)
