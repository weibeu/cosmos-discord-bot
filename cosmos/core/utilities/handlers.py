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

import json

import yaml


class FileHandler(object):

    @staticmethod
    def get_file_data(path):
        file_data = dict()
        file = open(path)
        if path.endswith(".json"):
            file_data = json.load(file)
        elif path.endswith(".yaml") or path.endswith(".yml"):
            file_data = yaml.safe_load(file)
        else:
            pass
        return file_data  # dict
