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

from . import configs


class ConfigHandler(object):

    def __init__(self):
        self.__fetch_configs()

    def __fetch_configs(self):
        for string in dir(configs):
            attr = getattr(configs, string)
            if hasattr(attr, "NAME") and hasattr(attr, "PATH") and (attr.PATH or attr.NAME):
                self.__setattr__(attr.NAME, attr())
