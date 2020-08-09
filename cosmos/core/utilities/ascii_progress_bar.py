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

from collections import UserString


class StaticProgressBar(UserString):

    BASE = "▢"
    FILL = "▣"

    DEFAULT_WIDTH = 40

    def __init__(self, value, max_value, width=DEFAULT_WIDTH):
        if value > max_value:
            raise ValueError
        progress = self.FILL * round((value/max_value)*width)
        base = self.BASE * (width - len(progress))
        progress_bar = progress + base
        super().__init__(progress_bar)
